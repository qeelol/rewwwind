from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from flask_mail import Message
from .models import MailingList, MailingPost
from .forms import NewsletterForm
from .roleDecorator import role_required
from . import db, mail
from dotenv import load_dotenv
import os

load_dotenv()

newsletter = Blueprint('newsletter', __name__)
# Newsletter page

def send_newsletter(form):
  mailing_list = MailingList.query.all()
  mailing_count = MailingList.query.count()
    
  recipients = [subscriber.email for subscriber in mailing_list]
    
  if not recipients or mailing_count == 0:
    flash('No subscribers in the mailing list.', 'error')
    return False
    
  try:
    # Create message
    msg = Message(
      subject=form.title.data, 
      sender=('Rewwwind', 'rewwwindmail@gmail.com'),
      bcc=recipients,
      body=form.description.data
    )

    # Send message
    mail.send(msg)
    flash('Newsletter sent successfully!', 'success')
    return True
  except Exception as e:
    current_app.logger.error(f"Newsletter sending failed: {str(e)}")
    flash('Failed to send newsletter. Please try again.', 'error')
    return False

@newsletter.route('/newsletter', methods=['GET', 'POST'])
@login_required
@role_required(2, 3)
def newsletter_page():
  form = NewsletterForm()
  subscribers = MailingList.query.all()

  posts_count = MailingPost.query.count()
    
  if form.validate_on_submit():
    if send_newsletter(form):

      mailingPost = MailingPost(
        title=form.title.data,
        description=form.description.data
      )

      db.session.add(mailingPost)
      try:
        db.session.commit()
        return redirect(url_for('newsletter.newsletter_page'))
      except Exception as e: # debug
        print(e)
        db.session.rollback()
        flash('An error occurred while creating the post.', 'error')

      return redirect(url_for('newsletter.newsletter_page'))

  return render_template("dashboard/newsletter/newsletter.html", user=current_user, form=form, subscribers=subscribers, posts_count=posts_count)

@newsletter.route('/newsletter/delete-subscriber/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required(2, 3)
def delete_subscriber(id):
  selected_subscriber = MailingList.query.get_or_404(id)

  if selected_subscriber:
    db.session.delete(selected_subscriber)
    db.session.commit()
    flash("Subscriber deleted.", "success")
    return redirect(url_for('newsletter.newsletter_page'))
  else:
    flash("Invalid subscriber or unauthorized access.", "error")
    return redirect(url_for('newsletter.newsletter_page'))