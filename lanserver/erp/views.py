import csv
import os
from zipfile import ZipFile
from django.core.mail import send_mail, EmailMessage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import EmailForm
from .models import Email 
import logging

def send_email(request):
    logger = logging.getLogger(__name__)

    if request.method == 'POST':
        form = EmailForm(request.POST, request.FILES)
        if form.is_valid():

            from_email = form.cleaned_data['from_email']
            to_email = form.cleaned_data['to_email']
            subject = form.cleaned_data['subject']
            body = form.cleaned_data['body']

            if to_email.endswith('@localhost'):

                email = EmailMessage(
                    subject,
                    body,
                    from_email,
                    [to_email],
                )

                for file in request.FILES.getlist('attachments'):
                    email.attach(file.name, file.read(), file.content_type)

                # send the all india LAN email immediately
                email.send()

            else:
                # keep the outside emails in a file for transfering mannually once in a day
                
                email_instance = Email.objects.create(
                    sender=from_email,
                    recipient=to_email,
                    subject=subject,
                    body=body,
                )

                # save attachments to the folder containing all zips

                attachments_folder = f'attachments/{email_instance.id}/'
                os.makedirs(attachments_folder, exist_ok=True)
                # print(request.FILES.getlist('attachments'))
                # logger.info(request.FILES.getlist('attachments'))

                for attachment in request.FILES.getlist('attachments'):
                    print(attachment.name)
                    logger.info(attachment.name)

                    attachment_path = os.path.join(attachments_folder, attachment.name)
                    with open(attachment_path, 'wb') as destination:
                        for chunk in attachment.chunks():
                            destination.write(chunk)

                zip_filename = f'attachments/{email_instance.id}.zip'
                with ZipFile(zip_filename, 'w') as zip_file:
                    for attachment in os.listdir(attachments_folder):
                        attachment_path = os.path.join(attachments_folder, attachment)
                        zip_file.write(attachment_path, attachment)

                with open('outbound_emails.csv', 'a', newline='') as csvfile:
                    email_writer = csv.writer(csvfile)
                    email_writer.writerow([email_instance.id, from_email, to_email, subject, body])

                # for attachment in os.listdir(attachments_folder):
                #     attachment_path = os.path.join(attachments_folder, attachment)
                #     os.remove(attachment_path)
                # os.rmdir(attachments_folder)

            return redirect('success')  
    else:
        form = EmailForm()

    return render(request, 'send_email.html', {'form': form})

def success_view(request):
    return render(request, 'success.html') 