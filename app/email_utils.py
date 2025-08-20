import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
import os

class EmailSender:
    """Email sender utility for verification emails"""
    
    def __init__(self):
        self.smtp_server = 'sandbox.smtp.mailtrap.io'
        self.smtp_port = 2525
        self.username = 'e8d2186c74a492'
        self.password = '0b4f93123cd1e5'
        self.use_tls = True
        self.use_ssl = False
    
    def send_verification_email(self, to_email, verification_code, user_name):
        """Send verification email with 6-digit code"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = 'noreply@otithi.com'
            msg['To'] = to_email
            msg['Subject'] = 'Verify Your Email - Otithi'
            
            # Email body
            body = f"""
            <html>
            <body>
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                        <h1 style="margin: 0; font-size: 28px;">অ. Otithi</h1>
                        <p style="margin: 10px 0 0 0; font-size: 16px;">A Bangladeshi Hospitality Platform</p>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; border: 1px solid #e9ecef;">
                        <h2 style="color: #333; margin-bottom: 20px;">Welcome to Otithi!</h2>
                        
                        <p style="color: #666; line-height: 1.6; margin-bottom: 20px;">
                            Hi <strong>{user_name}</strong>,<br><br>
                            Thank you for registering with Otithi! To complete your registration and verify your email address, 
                            please use the verification code below:
                        </p>
                        
                        <div style="background: #28a745; color: white; padding: 20px; border-radius: 8px; text-align: center; margin: 30px 0;">
                            <h1 style="margin: 0; font-size: 36px; letter-spacing: 5px; font-family: 'Courier New', monospace;">
                                {verification_code}
                            </h1>
                            <p style="margin: 10px 0 0 0; font-size: 14px;">Your 6-digit verification code</p>
                        </div>
                        
                        <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 6px; margin: 20px 0;">
                            <p style="margin: 0; color: #856404; font-size: 14px;">
                                <strong>Important:</strong> This code will expire in 24 hours. 
                                If you didn't request this verification, please ignore this email.
                            </p>
                        </div>
                        
                        <p style="color: #666; line-height: 1.6; margin-bottom: 20px;">
                            Once verified, you'll be able to:
                        </p>
                        
                        <ul style="color: #666; line-height: 1.6; margin-bottom: 20px;">
                            <li>Access your full account features</li>
                            <li>Book accommodations</li>
                            <li>List your properties (if you're a host)</li>
                            <li>Send and receive messages</li>
                            <li>Manage your bookings and reviews</li>
                        </ul>
                        
                        <p style="color: #666; line-height: 1.6; margin-bottom: 30px;">
                            If you have any questions or need assistance, please don't hesitate to contact our support team.
                        </p>
                        
                        <div style="text-align: center; margin-top: 30px;">
                            <p style="color: #999; font-size: 12px; margin: 0;">
                                Best regards,<br>
                                The Otithi Team
                            </p>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin-top: 20px; color: #999; font-size: 12px;">
                        <p>© 2025 Otithi. All rights reserved.</p>
                        <p>This email was sent to {to_email}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            return self._send_email(msg)
            
        except Exception as e:
            print(f"Error creating verification email: {e}")
            return False
    
    def send_welcome_email(self, to_email, user_name):
        """Send welcome email after successful verification"""
        try:
            msg = MIMEMultipart()
            msg['From'] = 'noreply@otithi.com'
            msg['To'] = to_email
            msg['Subject'] = 'Welcome to Otithi - Your Account is Verified!'
            
            body = f"""
            <html>
            <body>
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                        <h1 style="margin: 0; font-size: 28px;">অ. Otithi</h1>
                        <p style="margin: 10px 0 0 0; font-size: 16px;">A Bangladeshi Hospitality Platform</p>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; border: 1px solid #e9ecef;">
                        <h2 style="color: #333; margin-bottom: 20px;">🎉 Welcome to Otithi!</h2>
                        
                        <p style="color: #666; line-height: 1.6; margin-bottom: 20px;">
                            Hi <strong>{user_name}</strong>,<br><br>
                            Congratulations! Your email has been successfully verified. Your Otithi account is now fully active 
                            and ready to use.
                        </p>
                        
                        <div style="background: #d4edda; border: 1px solid #c3e6cb; padding: 20px; border-radius: 8px; margin: 30px 0;">
                            <h3 style="color: #155724; margin: 0 0 15px 0;">✅ Account Verified Successfully</h3>
                            <p style="color: #155724; margin: 0; line-height: 1.6;">
                                You can now access all features of your Otithi account, including booking accommodations, 
                                listing properties, and connecting with other users.
                            </p>
                        </div>
                        
                        <h3 style="color: #333; margin-bottom: 15px;">🚀 What's Next?</h3>
                        
                        <div style="background: white; border: 1px solid #e9ecef; border-radius: 8px; padding: 20px; margin: 20px 0;">
                            <h4 style="color: #28a745; margin: 0 0 15px 0;">For Guests:</h4>
                            <ul style="color: #666; line-height: 1.6; margin: 0; padding-left: 20px;">
                                <li>Browse and book amazing accommodations</li>
                                <li>Read reviews and ratings</li>
                                <li>Save your favorite listings</li>
                                <li>Message hosts directly</li>
                                <li>Manage your bookings and reviews</li>
                            </ul>
                        </div>
                        
                        <div style="background: white; border: 1px solid #e9ecef; border-radius: 8px; padding: 20px; margin: 20px 0;">
                            <h4 style="color: #007bff; margin: 0 0 15px 0;">For Hosts:</h4>
                            <ul style="color: #666; line-height: 1.6; margin: 0; padding-left: 20px;">
                                <li>List your properties for guests</li>
                                <li>Set your own prices and availability</li>
                                <li>Manage bookings and guest communications</li>
                                <li>Earn money by hosting travelers</li>
                                <li>Build your hosting reputation</li>
                            </ul>
                        </div>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="http://127.0.0.1:5000" style="background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">
                                Start Exploring Otithi
                            </a>
                        </div>
                        
                        <p style="color: #666; line-height: 1.6; margin-bottom: 20px;">
                            We're excited to have you as part of the Otithi community! If you have any questions or need help 
                            getting started, our support team is here to help.
                        </p>
                        
                        <div style="text-align: center; margin-top: 30px;">
                            <p style="color: #999; font-size: 12px; margin: 0;">
                                Best regards,<br>
                                The Otithi Team
                            </p>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin-top: 20px; color: #999; font-size: 12px;">
                        <p>© 2025 Otithi. All rights reserved.</p>
                        <p>This email was sent to {to_email}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            return self._send_email(msg)
            
        except Exception as e:
            print(f"Error creating welcome email: {e}")
            return False
    
    def _send_email(self, msg):
        """Send email using SMTP"""
        try:
            # Create SMTP connection
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            
            if self.use_tls:
                server.starttls()
            
            # Login
            server.login(self.username, self.password)
            
            # Send email
            server.send_message(msg)
            server.quit()
            
            print(f"Email sent successfully to {msg['To']}")
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def test_connection(self):
        """Test SMTP connection"""
        try:
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            
            if self.use_tls:
                server.starttls()
            
            server.login(self.username, self.password)
            server.quit()
            
            print("SMTP connection test successful!")
            return True
            
        except Exception as e:
            print(f"SMTP connection test failed: {e}")
            return False
