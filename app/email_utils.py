from flask_mail import Message
from flask import current_app, flash

from .extensions import mail


# Send Email
def send_email(subject, recipients, html_body):
    try:
        msg = Message(
            subject=subject,
            recipients=recipients,
            sender=current_app.config["MAIL_DEFAULT_SENDER"]
        )

        msg.html = html_body
        try:
            mail.send(msg)
        except Exception:
            print("Email failed")
        return True

    except Exception as e:
        current_app.logger.error(f"Email sending failed: {e}")
        return False


# Email Template
def build_email_template(
    title,
    content,
    button_text=None,
    button_link=None,
    is_emergency=False
):

    # Dynamic UI Colors
    header_color = "#dc3545" if is_emergency else "#0d6efd"
    button_color = "#dc3545" if is_emergency else "#0d6efd"

    emergency_badge = ""
    if is_emergency:
        emergency_badge = """
        <div style="
            display:inline-block;
            background:#ff4d4f;
            color:white;
            padding:6px 14px;
            font-size:12px;
            font-weight:600;
            border-radius:20px;
            margin-bottom:15px;
        ">
            🚨 EMERGENCY REQUEST
        </div>
        """

    # Button HTML
    button_html = ""
    if button_text and button_link:
        button_html = f"""
        <div style="text-align:center; margin-top:30px;">
            <a href="{button_link}"
               style="
                    background:{button_color};
                    color:white;
                    padding:14px 28px;
                    text-decoration:none;
                    border-radius:8px;
                    font-weight:600;
                    display:inline-block;
                    box-shadow:0 4px 12px rgba(0,0,0,0.15);
                    font-size:14px;
               ">
                {button_text}
            </a>
        </div>
        """

    # Final HTML Template
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
    </head>

    <body style="
        margin:0;
        padding:0;
        background-color:#f4f6f9;
        font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
    ">

        <div style="
            max-width:600px;
            margin:40px auto;
            background:white;
            border-radius:14px;
            overflow:hidden;
            box-shadow:0 10px 25px rgba(0,0,0,0.08);
        ">

            <!-- HEADER -->
            <div style="
                background:{header_color};
                padding:30px;
                text-align:center;
                color:white;
            ">
                <h1 style="margin:0; font-size:24px; letter-spacing:0.5px;">
                    BloodCare+
                </h1>
                <p style="margin:6px 0 0; font-size:14px; opacity:0.9;">
                    {title}
                </p>
            </div>

            <!-- BODY -->
            <div style="
                padding:30px;
                color:#333;
                font-size:15px;
                line-height:1.7;
            ">

                {emergency_badge}

                {content}

                {button_html}

            </div>

            <!-- FOOTER -->
            <div style="
                background:#f1f3f6;
                padding:20px;
                text-align:center;
                font-size:12px;
                color:#777;
            ">
                © 2026 BloodCare+ | Blood Donation & Request Management System
                <br><br>
                <span style="color:#999;">
                    This is an automated notification from BloodCare+. Please do not reply to this email.
                </span>
            </div>

        </div>

    </body>
    </html>
    """