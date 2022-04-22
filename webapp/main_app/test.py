from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

string = "We're not gonna lose"

string_cleaned = string.lower()  # Remove capitalization
string_cleaned = string_cleaned.replace('[^\w\s]', '')  # Removes extra whitespaces
string_cleaned = string_cleaned.replace('@[A-Za-z0-9]+', '')  # Removes any tags using @
string_cleaned = string_cleaned.replace('\n', '')

analyzer = SentimentIntensityAnalyzer()
vs = analyzer.polarity_scores(string_cleaned)

print(string)
print(string_cleaned)

print(vs)