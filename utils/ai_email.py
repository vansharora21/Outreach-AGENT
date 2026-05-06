from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

# Fallback template if OpenAI API fails
FALLBACK_EMAIL_TEMPLATE = """Hi {restaurant_name},

I hope this email finds you well. I'm a web developer specializing in creating modern, responsive websites for restaurants.

I noticed that {restaurant_name} doesn't currently have an online presence. In today's digital world, a professional website can significantly boost your business by:

• Making it easier for customers to find you online
• Showcasing your menu and dining experience
• Allowing online reservations and orders
• Building trust with potential customers

I'd love to help you establish a strong online presence with a custom-built website tailored to your restaurant's unique style and needs.

Would you be open to a quick conversation about how a website could benefit your business?

Looking forward to hearing from you!

Best regards"""

# Follow-up email templates
FOLLOWUP_EMAIL_TEMPLATE = """Hi {restaurant_name},

I hope this email finds you well. I sent you a message a few days ago about creating a professional website for {restaurant_name}.

I wanted to follow up because I genuinely believe a website could make a real difference for your business:

✓ More visibility on Google
✓ Show customers your menu & hours
✓ Easier online ordering
✓ Build credibility with reservations

I'd love to discuss how we can make this happen. Are you open to a quick chat?

Best regards"""


def generate_email(restaurant_name: str, followup_template: str = None) -> str:
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
            Write a polite cold email to a restaurant owner.
            The restaurant name is {restaurant_name}.
            The restaurant does NOT have a website.

            Offer a modern frontend website.
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
        print(f"⚠️ OpenAI API error: {e}")
        print("💡 Using fallback email template instead...\n")
        
        if followup_template:
            return FOLLOWUP_EMAIL_TEMPLATE.format(restaurant_name=restaurant_name)
        else:
            return FALLBACK_EMAIL_TEMPLATE.format(restaurant_name=restaurant_name)
