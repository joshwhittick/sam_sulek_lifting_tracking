# Sam Sulek Lifting Tracking

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://samsulekliftingtracking.streamlit.app/)

This project tracks the lifting progress of Sam Sulek by scraping his YouTube channel, analyzing the data, and presenting it in an interactive Streamlit web application.

## Features

- **Automated YouTube Scraping:** Automatically fetches new video data from Sam Sulek's YouTube channel.
- **Data Cleaning and Enrichment:** Cleans and enriches the scraped data by extracting relevant information like the lifting event, day number, and specific lifts performed.
- **Interactive Data Visualization:** Presents the data in an interactive Streamlit application with features like:
    - **Lifting Pie Charts:** Visualizes the frequency of different lifts and muscle groups.
    - **Event Durations:** Shows the duration of each of Sam Sulek's lifting phases (e.g., "Winter Bulk," "Fall Cut").
    - **Lifting Calendars:** Displays the lifting data on interactive calendar heatmaps.
- **Up-to-Date Data:** Allows users to fetch the most recent data with the click of a button.

## How to Use

1. **Visit the Streamlit App:** The easiest way to use the application is to visit the [Streamlit App](https://samsulekliftingtracking.streamlit.app/).
2. **Get Most Recent Data:** Click the "Get Most Recent Data" button to check for and fetch new videos.
3. **Analyze Data:** Click the "Analyse" button to view the latest data analysis, including pie charts, event durations, and lifting calendars.

## Data Scraping and Analysis

The project uses the following process to scrape and analyze the data:

1. **Scraping:** The `scrape.py` script uses `yt-dlp` to scrape video titles and URLs from Sam Sulek's YouTube channel.
2. **Data Cleaning:** The `analyse.py` script cleans and enriches the data by:
    - **Parsing Titles:** Using regular expressions to extract the lifting event, day number, and specific lifts from the video titles.
    - **Standardizing Lifts:** Using the `lift_types.json` file to standardize the names of different lifts.
3. **Data Analysis:** The `analyse.py` script also performs the data analysis, including:
    - **Calculating Lift Frequencies:** Counting the occurrences of each lift and muscle group.
    - **Determining Event Durations:** Calculating the duration of each lifting phase.
4. **Data Visualization:** The `main.py` script uses Streamlit to create the interactive web application and `heat_maps.py` to generate the calendar plots.

## Running Locally

To run the project locally, follow these steps:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/sam_sulek_lifting_tracking.git
   cd sam_sulek_lifting_tracking
   ```
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Streamlit App:**
   ```bash
   streamlit run main.py
   ```

## To-Do

- [ ] Add more advanced data analysis features, such as tracking progress on specific lifts over time.
- [ ] Improve the UI/UX of the Streamlit application.
- [ ] Add a database to store the data instead of a JSON file.
- [ ] Create more detailed documentation for each script.

## Contributing

Contributions are welcome! If you have any ideas for new features or improvements, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.