
import win32com.client as win32

def send_email_simple (mail_to,subject,bodymsg,html_body,attachment):

    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    mail.To = mail_to
    mail.Subject = subject
    mail.Body = bodymsg
    mail.HTMLBody = html_body #this field is optional

    if attachment:

    # To attach a file to the email (optional):
    # attachment  = "Path to the attachment"
        mail.Attachments.Add(attachment)

    mail.Send()

    return
