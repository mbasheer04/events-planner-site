README:

The giginator is a website for planning and displaying events. Users are able to view upcoming events, as well as purchase and
store tickets for these events.

To run the website locally, run the setup.sh file or the run.sh file. This will host the website on a local host port,
and can be accessed through the url http://127.0.0.1:58490/

Below are some detailed features of the website, including some implementation details and internal aspects.

Header: The header contains several link buttons which vary depending on whether the user is logged in. The Home button is
        the main way to reach the home page, and it has a bright blue colour scheme to increase accessibility for colorblind
        users. The logo in the top-left also directs to the home page for convenience. Users can choose to login or
        register using the respective buttons. Logged in users can select "My Tickets" and "My Events" alongside the Logout
        button in the top right. All the header buttons decrease in opacity or change colour when hovered over to make them
        easier to recognise. The styling for the header is stored in a separate css file. 

Footer: The footer is a simple strip with a small logo in the centre. The colour scheme matches the header and the content,
        and the footer uses a flex-box to stay at the bottom of the page. Both the Header and Footer are added to the pages
        through the Jinja2 include method.

Homepage: The Home Page contains a short desciption of the website inside the content box. Webkit is used to style the titles
          of the pages.

Registration: The Registration page contains a form with inputs for the user's details. It uses a substantial amount of JQuery 
              to validate the inputs by checking if: all input boxes are filled in, the username is the correct length, the
              password contains lowercase,uppercase and numerical characters, and that the passwords match. If any of these
              are false, the page displays an error message under the respective input box and plays a shaking animation for
              that input box. Once the data has been validated by JQuery, the usernames and emails are checked to see if they
              are unique, otherwise the user is redirected to the same page. If the organiser key input box is left blank, the
              website assumes that the user is an attendee. If the organiser key is invalid, it will display an error
              message, but if it is valid the website will record the user as an organiser. 

Email Verification: Once registration is complete, the program then sends an email to the user's email with a verification 
            code, which is entered into the email verification page. If the verification codes match, the user is added to
            the database. The user's password is hashed before being stored to increase security of data.

Login: The Login page is very similar to registration, with the same styling of error messages. Once login is complete, the
       login_user method is called to store the user's data within the session.

Browse: The Browse page shows all the available events to both guests and users. The page shows all available events, followed
        by booked events and sold-out events. Users can buy a ticket for an event from this page, although guests will be
        redirected to the login page. Events that have less than 5% availability left will have text that displays the number of tickets remaining. These events will also send an email to their organisers that the events are reaching capacity.

My Tickets: This page shows all the tickets currently owned by the user. The user can View Ticket or Sell Ticket. The View
            Ticket option opens up a popup box with the event name and the barcode for the ticket, generated through AJAX. The
            barcode uses SVG to represent the serial number of the barcode as an image. Sell Ticket deletes the ticket from 
            the database, removing it from the user's MyTickets page. Non-ticket UserEvents are also shown here, because organisers are given their own barcode and tickets for events that they are managing. However, these do not count towards the availability.

My Events: This page shows all the events that the user is an organiser for. On this page, Attendees can manage events that 
           they have been promoted to organiser for, whereas Website Organisers can also create events and promote users.
           Organisers can delete an event, which will delete all tickets and send an email to all attendees that the event has been deleted.

Tickets: The interface for tickets uses a single HTML template (ticket.HTML). This is dropped into other templates using the 
         Jinja2 include method.

Database Schema: The database for this website consists of 3 tables: User, Event and UserEvent. User stores all the information
                 about each user (fullname,username,email,password,isOrganiser). isOrganiser is used to distinguish between attendees and organisers: Organisers are able to create events and promote users, whereas attendees can only modify events that they have been promoted to organiser for. Event stores all the information about each
                 event (eventname,date,time,duration,capacity). UserEvent is an association table that is used to join the 
                 many-to-many relationship of User and Event. It has user_id and event_id as composite primary keys to join
                 the two tables, alongside isTicket and serial_number. isTicket is a boolean that determines if the
                 relationship between the user and the event is a ticket or that of an organiser (an organiser is related to
                 its event, but will not count as a ticket). This allows attendees to manage events, and organisers to buy tickets. serial_number is used solely for barcodes, and is created by a random number generator.

----Extra Functionality----

Pop-up: When the "buy ticket" or "sell ticket" buttons are selected, a popup screen appears. This is the first extra 
        functionality of the webpage. This feature was built using JQuery and dynamically loads up the page on top without
        any redirects. If the user clicks on the transparent background around the box, the popup box will close. It can also 
        be closed by clicking the cancel button. All popups on the webpage use the same two elements to give the basis of
        the popup page (popup and popup-background) with only the contents of the popup differing. Also, the page has a zoom
        animation created using animation keyframes in CSS. The advantages of a popup screen is that it reduces the amount of
        cluttering on a single page and allows the elements to be more spaced out. This is also very beneficial for people with poor motor skills since the popup menu allows for larger buttons that are easier to click.

Promoting Users: The second extra functionality for the webpage is the ability to promote users to Website Organisers OR
                 Event Organisers. Event Organisers are users that can manage a particular event. Website Organisers are users 
                 that can create events, promote users, but are not necessarily able to manage every event. Users can become 
                 Event Organisers by either being promoted by a Website Organiser, or by creating the event themselves 
                 (requires them to already be a Website Organiser). Users can become Website Organisers by entering the 
                 correct organiserKey during registration, or by being promoted by another Website Organiser. This can be done in the myEvents page. The advantages of this is that an attendee can be given permission to organise certain events without having access to the all the features of a Website Organiser.

              


