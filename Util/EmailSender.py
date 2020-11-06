
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








#
# def send_email_simple_attached_image(mail_to,img_data):
#
#     msg = EmailMessage()
#     msg.add_header('Content-Type', 'text/html')
#     msg.set_content(f'''<html>
#     <head></head>
#     <body>
#     <img src="data:image/{'png'};base64, {b64encode(img_data).decode('ascii')}">
#     </body>
#     </html>''')
#
#     s = smtplib.SMTP('localhost')
#     s.starttls()
#     s.login(...)
#     s.sendmail(msg['From'], [mail_to], msg.as_string())
#     s.quit()
#
#     return
#
#
#
#
#
#
#
# def send_email_embed_img(mail_to,mail_from,subject,bodymsg,html_body,attachment):
#     from email.message import EmailMessage
#     from email.utils import make_msgid
#     import mimetypes
#
#     msg = EmailMessage()
#
#     # generic email headers
#     msg['Subject'] = subject
#     msg['From'] = mail_from
#     msg['To'] = mail_to
#
#     # set the plain text body
#     msg.set_content(bodymsg)
#
#     # now create a Content-ID for the image
#     # image_cid = make_msgid(domain='xyz.com')
#     image_cid = make_msgid()
#
#     # if `domain` argument isn't provided, it will
#     # use your computer's name
#
#     # set an alternative html body
#     msg.add_alternative("""\
#     <html>
#         <body>
#             <p>This is an HTML body.<br>
#                It also has an image.
#             </p>
#             <img src="cid:{image_cid}">
#         </body>
#     </html>
#     """.format(image_cid=image_cid[1:-1]), subtype='html')
#     # image_cid looks like <long.random.number@xyz.com>
#     # to use it as the img src, we don't need `<` or `>`
#     # so we use [1:-1] to strip them off
#
#     # now open the image and attach it to the email
#     with open(attachment, 'rb') as img:
#         # know the Content-Type of the image
#         maintype, subtype = mimetypes.guess_type(img.name)[0].split('/')
#
#         # attach it
#         msg.get_payload()[1].add_related(img.read(),
#                                          maintype=maintype,
#                                          subtype=subtype,
#                                          cid=image_cid)
#
#     smtp = smtplib.SMTP()
#     smtp.sendmail()
#     smtp.quit()
#
#     return