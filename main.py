from bookstore import create_app, render_template

app = create_app()

@app.route('/about')
def about_page():
    return render_template('about.html')
@app.route('/contact')
def contact_page():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)
@app.route('/bookDepartment')
def book_page():
    return render_template('bookDepartment.html')

if __name__ == '__main__':
    app.run(debug=True)
