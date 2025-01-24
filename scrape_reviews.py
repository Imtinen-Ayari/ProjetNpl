import requests
from bs4 import BeautifulSoup
import csv

def scrape_book_reviews(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the reviews section and extract review text
    reviews = soup.select('.review')  # This is a placeholder, adjust the selector
    reviews_text = []

    for review in reviews:
        review_text = review.get_text(strip=True)
        reviews_text.append(review_text)

    # If no reviews, return a placeholder text
    if not reviews_text:
        reviews_text.append("No reviews available.")

    return " | ".join(reviews_text)  # Join multiple reviews if needed


def scrape_books_reviews(base_url, max_books=400):
    current_page = 1
    books_data = []
    ratings_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}

    while len(books_data) < max_books:
        url = f"{base_url}catalogue/page-{current_page}.html"
        response = requests.get(url)

        # Check if the page exists
        if response.status_code != 200:
            print(f"Page {current_page} does not exist. Stopping...")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        books = soup.select('article.product_pod')

        for book in books:
            if len(books_data) >= max_books:
                break

            title = book.h3.a['title']
            rating_class = book.select_one('.star-rating')['class'][1]
            rating = ratings_map.get(rating_class, 0)
            
            # Scrape individual book reviews
            book_url = base_url + book.h3.a['href']
            reviews = scrape_book_reviews(book_url)
            
            books_data.append({'title': title, 'rating': rating, 'reviews': reviews})

        current_page += 1  # Move to the next page

    return books_data


def calculate_average_rating(books_data):
    total_rating = sum(book['rating'] for book in books_data)
    average_rating = total_rating / len(books_data) if books_data else 0
    return round(average_rating, 2)


def save_to_csv(filename, books_data, average_rating):
    # Open the file in write mode
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        # Define the fieldnames (columns)
        fieldnames = ["title", "rating", "reviews", "average_rating"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()  # Write header row
        for book in books_data:
            # Add average rating to each row of data
            book['average_rating'] = average_rating
            writer.writerow(book)  # Write data row


if __name__ == "__main__":
    base_url = "http://books.toscrape.com/"
    max_books = 400  # Number of records to scrape
    output_file = "books_dataset_with_reviews_and_average.csv"

    print(f"Scraping data to create a dataset with {max_books} records...")
    books_data = scrape_books_reviews(base_url, max_books)

    print("Calculating average rating...")
    avg_rating = calculate_average_rating(books_data)

    print(f"Saving data to {output_file}...")
    save_to_csv(output_file, books_data, avg_rating)

    print(f"Dataset with {len(books_data)} records, average rating {avg_rating}, and reviews saved successfully!")
