import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import re
from wordcloud import WordCloud

matplotlib.use('Agg')

cleaned_data = pd.read_excel('Week_4_Cleaned.xlsx')

notes = cleaned_data['Notes'].dropna().astype(str)

filler_words = {
    'the', 'and', 'to', 'a', 'of', 'in', 'on', 'for', 'at',
    'by', 'an', 'be', 'is', 'with', 'as', 'that'
}


def clean_and_tokenize(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    words = [w for w in text.split() if w not in filler_words]
    return words


cleaned_tokenized = notes.apply(clean_and_tokenize)

all_words = pd.Series([w for words in cleaned_tokenized for w in words])
word_counts = all_words.value_counts()

top_15 = word_counts.sort_values(ascending=False).head(15)
print('Top 15 Keywords:')
print(top_15)

freq_df = word_counts.rename_axis('keyword').reset_index(name='count')
freq_df.to_excel('frequency_table.xlsx', index=False)

wc = WordCloud(
    width=1600,
    height=900,
    background_color="white",
    collocations=False
).generate_from_frequencies(word_counts.to_dict())

plt.figure(figsize=(12, 7))
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.tight_layout()
plt.savefig('wordcloud.png', dpi=300, bbox_inches='tight')
