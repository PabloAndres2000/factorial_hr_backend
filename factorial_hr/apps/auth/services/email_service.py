# factorial_hr/apps/auth/services/email_service.py
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


class EmailService:
    """
    Servicio para enviar correos electrónicos
    """
    
    @staticmethod
    def send_welcome_email(user_email: str, user_name: str, verification_token: str = None) -> bool:
        """
        Envía un correo de bienvenida al usuario registrado con link de verificación
        
        Args:
            user_email: Email del usuario
            user_name: Nombre del usuario
            verification_token: Token de verificación (opcional, si no se proporciona, no incluye link)
            
        Returns:
            bool: True si el correo fue enviado exitosamente, False en caso contrario
        """
        try:
            subject = '¡Bienvenido a Factorial HR! - Verifica tu cuenta'
            
            # Generar link de verificación si hay token
            verification_link = ""
            if verification_token:
                verification_link = f"{settings.FRONT_URL}/verify-email?token={verification_token}"
            
            # Mensaje en HTML
            html_message = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #4CAF50;">¡Bienvenido a Factorial HR, {user_name}!</h2>
                        <p>Tu cuenta ha sido creada exitosamente.</p>
                        <p>Tu correo electrónico registrado es:</p>
                        <p style="background-color: #f4f4f4; padding: 10px; border-radius: 5px;">
                            <strong>{user_email}</strong>
                        </p>
            """
            
            # Agregar sección de verificación si hay token
            if verification_token:
                html_message += f"""
                        <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0;">
                            <p style="margin: 0; color: #856404;">
                                <strong>⚠️ Verificación requerida</strong>
                            </p>
                            <p style="margin: 10px 0 0 0; color: #856404;">
                                Para activar tu cuenta y acceder a todas las funcionalidades, 
                                debes verificar tu correo electrónico.
                            </p>
                        </div>
                        <p style="text-align: center; margin: 30px 0;">
                            <a href="{verification_link}" 
                               style="background-color: #4CAF50; color: white; padding: 14px 28px; 
                                      text-decoration: none; border-radius: 5px; display: inline-block;
                                      font-weight: bold; font-size: 16px;">
                                ✓ Verificar mi correo electrónico
                            </a>
                        </p>
                        <p style="font-size: 14px; color: #666; text-align: center;">
                            O copia y pega este enlace en tu navegador:
                        </p>
                        <p style="font-size: 12px; color: #999; word-break: break-all; text-align: center;">
                            {verification_link}
                        </p>
                        <p style="font-size: 12px; color: #999; text-align: center;">
                            Este enlace expirará en 24 horas.
                        </p>
                """
            else:
                html_message += """
                        <p>Ahora puedes acceder a nuestra plataforma.</p>
                """
            
            html_message += """
                        <p>Si tienes alguna pregunta, no dudes en contactarnos.</p>
                        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                        <p style="font-size: 12px; color: #777;">
                            Este es un correo automático, por favor no respondas a este mensaje.
                        </p>
                    </div>
                </body>
            </html>
            """
            
            # Mensaje en texto plano (fallback)
            plain_message = f"""
            ¡Bienvenido a Factorial HR, {user_name}!
            
            Tu cuenta ha sido creada exitosamente.
            
            Tu correo electrónico registrado es: {user_email}
            """
            
            if verification_token:
                plain_message += f"""
            
            ⚠️ VERIFICACIÓN REQUERIDA
            
            Para activar tu cuenta y acceder a todas las funcionalidades, 
            debes verificar tu correo electrónico.
            
            Haz clic en el siguiente enlace para verificar tu cuenta:
            {verification_link}
            
            Este enlace expirará en 24 horas.
                """
            else:
                plain_message += """
            
            Ahora puedes acceder a nuestra plataforma.
                """
            
            plain_message += """
            
            Si tienes alguna pregunta, no dudes en contactarnos.
            
            ---
            Este es un correo automático, por favor no respondas a este mensaje.
            """
            
            # Enviar el correo
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user_email],
                html_message=html_message,
                fail_silently=False,
            )
            
            return True
            
        except Exception as e:
            print(f"Error al enviar correo: {str(e)}")
            return False
    
    @staticmethod
    def send_password_reset_email(user_email: str, reset_token: str) -> bool:
        """
        Envía un correo para restablecer contraseña (método de ejemplo para futuro uso)
        
        Args:
            user_email: Email del usuario
            reset_token: Token de restablecimiento
            
        Returns:
            bool: True si el correo fue enviado exitosamente, False en caso contrario
        """
        try:
            subject = 'Restablece tu contraseña - Factorial HR'
            reset_link = f"{settings.FRONT_URL}/reset-password?token={reset_token}"
            
            html_message = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #4CAF50;">Restablece tu contraseña</h2>
                        <p>Has solicitado restablecer tu contraseña.</p>
                        <p>Haz clic en el siguiente enlace para continuar:</p>
                        <p style="margin: 20px 0;">
                            <a href="{reset_link}" 
                               style="background-color: #4CAF50; color: white; padding: 12px 24px; 
                                      text-decoration: none; border-radius: 5px; display: inline-block;">
                                Restablecer contraseña
                            </a>
                        </p>
                        <p style="font-size: 12px; color: #777;">
                            Si no solicitaste este cambio, puedes ignorar este correo.
                        </p>
                    </div>
                </body>
            </html>
            """
            
            plain_message = f"""
            Restablece tu contraseña
            
            Has solicitado restablecer tu contraseña.
            
            Visita el siguiente enlace para continuar: {reset_link}
            
            Si no solicitaste este cambio, puedes ignorar este correo.
            """
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user_email],
                html_message=html_message,
                fail_silently=False,
            )
            
            return True
            
        except Exception as e:
            print(f"Error al enviar correo: {str(e)}")
            return False

