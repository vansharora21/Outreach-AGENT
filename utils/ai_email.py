from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Fallback template if OpenAI API fails
FALLBACK_EMAIL_TEMPLATE = """Hi {restaurant_name},

I hope this email finds you well. I'm a web developer specializing in modern, responsive websites for growing businesses.

I had an idea for how a clearer digital presence could help {restaurant_name}:

- Make it easier for customers to find you online
- Clearly present your services and customer experience
- Make it simple to enquire or buy
- Build trust before a customer reaches out

I'd love to share a few ideas for a website tailored to your business and customers.

Would you be open to a quick conversation about how a website could benefit your business?

Looking forward to hearing from you!

Best regards"""

# Follow-up email templates
FOLLOWUP_EMAIL_TEMPLATE = """Hi {restaurant_name},

I hope this email finds you well. I sent you a message a few days ago about creating a professional website for {restaurant_name}.

I wanted to follow up because I believe a website could make a real difference for your business:

✓ More visibility on Google
✓ Show customers your services and hours
✓ Make it easier to enquire or buy
✓ Build credibility with reservations

I'd love to discuss how we can make this happen. Are you open to a quick chat?

Best regards"""


def generate_email(restaurant_name: str, followup_template: str = None, business_type: str = "restaurant") -> str:
    """
    Generate a personalized cold email for a restaurant.
    Falls back to template if OpenAI API fails.
    
    Args:
        restaurant_name: Name of the restaurant
        followup_template: Optional follow-up message template
    
    Returns:
        Personalized email body
    """
    try:
        if not client:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        business_label = business_type.replace("_", " ")
        if followup_template:
            prompt = f"""
            Write a personalized follow-up email to a restaurant owner.
            Restaurant name: {restaurant_name}
            
            Start with this message:
            {followup_template}
            
            Then add:
            - One specific benefit of having a website
            - A call-to-action to set up a brief call
            
            Keep it under 120 words total.
            Tone: professional and human.
            """
        else:
            prompt = f"""
            Write a polite cold email to a {business_label} owner.
            The business name is {restaurant_name}.

            Offer a modern website or digital presence improvement without claiming
            that the business lacks a website. Do not invent personal details.
            Do NOT mention pricing.
            Keep it under 120 words.
            Tone: professional and human.
            """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful sales assistant for web development."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        print("AI message generation unavailable; using the local fallback draft.\n")
        
        if followup_template:
            return FOLLOWUP_EMAIL_TEMPLATE.format(restaurant_name=restaurant_name)
        else:
            return FALLBACK_EMAIL_TEMPLATE.format(restaurant_name=restaurant_name)
