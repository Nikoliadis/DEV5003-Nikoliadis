from flask import Flask, render_template

app = Flask(__name__)

featured_items = [
    {"title": "Ancient Vase", "image": "https://static01.nyt.com/images/2017/08/01/nyregion/01-SEIZE-1/01-SEIZE-1-superJumbo.jpg"},
    {"title": "Renaissance Painting", "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSYQzhGI2Jnk42d8TP2E6D1nd5k3q3BqRpf7Q&s"},
    {"title": "Fossil Exhibit", "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSfAFES8nTb5_Q5_W-WADwCsPX875qEpFPF_w&s"}
]

upcoming_events = [
    {'title': 'New Exhibit Launch', 'date': 'January 17, 2025', 'description': 'Join us for the opening of our new art exhibit showcasing Renaissance masterpieces.'},
    {'title': 'Lecture on Ancient Civilizations', 'date': 'February 14, 2025', 'description': 'A special lecture exploring the cultures of Ancient Egypt and Greece.'},
    {'title': 'Museum Gala', 'date': 'March 8, 2025', 'description': 'An elegant evening with art, music, and fine dining to support the museum.'}
]

museum_overview = "Our museum is dedicated to preserving and showcasing historical artifacts, artwork, and exhibits from various time periods. Visit us for a journey through history."

@app.route('/')
def home():
    featured_items = [
        {'title': 'Ancient Vase', 'image': 'https://static01.nyt.com/images/2017/08/01/nyregion/01-SEIZE-1/01-SEIZE-1-superJumbo.jpg', 'description': 'A rare ancient vase from the 4th century.'},
        {'title': 'Renaissance Painting', 'image': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSYQzhGI2Jnk42d8TP2E6D1nd5k3q3BqRpf7Q&s', 'description': 'A beautiful painting from the Renaissance period.'},
        {'title': 'Fossil Exhibit', 'image': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSfAFES8nTb5_Q5_W-WADwCsPX875qEpFPF_w&s', 'description': 'Step into the past with our fossil collection.'}
    ]
    return render_template('home.html', featured_items=featured_items)



@app.route('/about')
def about():
    return render_template('about.html', museum_overview=museum_overview)

@app.route('/events')
def events():
    upcoming_events = [
        {'id': 1, 'title': 'Art Exhibition Opening', 'date': 'January 2025', 'description': 'Join us for the opening of the new art exhibition.'},
        {'id': 2, 'title': 'Museum Gala', 'date': 'February 2025', 'description': 'Tickets now available for our annual museum gala.'},
    ]
    return render_template('events.html', upcoming_events=upcoming_events)


@app.route('/exhibits')
def exhibits():
    exhibits = [
       {'title': 'Ancient Vase', 'image': 'https://static01.nyt.com/images/2017/08/01/nyregion/01-SEIZE-1/01-SEIZE-1-superJumbo.jpg', 'description': 'A rare ancient vase from the 4th century.'},
        {'title': 'Renaissance Painting', 'image': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSYQzhGI2Jnk42d8TP2E6D1nd5k3q3BqRpf7Q&s', 'description': 'A beautiful painting from the Renaissance period.'},
        {'title': 'Fossil Exhibit', 'image': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSfAFES8nTb5_Q5_W-WADwCsPX875qEpFPF_w&s', 'description': 'Step into the past with our fossil collection.'}
    ]
    return render_template('exhibits.html', exhibits=exhibits)


@app.route('/news')
def news():
    news_items = [
        {'title': 'New Exhibit Opens', 'date': 'December 2024', 'description': 'Join us for the opening of the new Egyptian Artifacts exhibit.'},
        {'title': 'Museum Gala Event', 'date': 'January 2025', 'description': 'Tickets are now available for our annual gala fundraiser.'},
    ]
    return render_template('news.html', news_items=news_items)

@app.route('/services')
def services():
    services = [
        {'title': 'Coffee Shop', 'description': 'Enjoy a warm cup of coffee at our in-house café.'},
        {'title': 'Gift Shop', 'description': 'Find unique souvenirs and art pieces from the museum store.'},
        {'title': 'Tour Guides', 'description': 'Our expert guides offer personalized tours for a deeper understanding of exhibits.'},
        {'title': 'Services for Disabled', 'description': 'We offer wheelchair access, braille signage, and more for our disabled visitors.'},
    ]
    return render_template('services.html', services=services)


if __name__ == '__main__':
    app.run(debug=True)
