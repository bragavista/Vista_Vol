
import win32com.client as win32
from base64 import b64encode
from email.message import EmailMessage
import smtplib

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

def send_email_embed_img(mail_to,sender,subject,html_body,image_path):

    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    mail.To = mail_to
    mail.Subject = subject
    attachment = mail.Attachments.Add(image_path)
    attachment.PropertyAccessor.SetProperty("http://schemas.microsoft.com/mapi/proptag/0x3712001F", "MyId1")
    mail.HTMLBody = html_body + "<html><body><img src=""cid:MyId1""></body></html>"
    mail.SentOnBehalfOfName = sender
    mail.GetInspector
    mail.Send()
    return




