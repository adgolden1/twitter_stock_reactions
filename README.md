# Measuring retro-diction in twitter stocks
The relationships between financial markets and social/news media are complex and pose a compelling set of problems for anyone with a professional or research interest in markets. One especially tantalizing angle is understanding time relationships between the two. Can movements in financial markets be predicted based on social media activity? Several banks and hedge funds have expressed interest in analyzing social media data, which is understandable considering the outsized effect that social media has had on the markets in the past year or two, for example the "Wall St. Bets" community and its role in a historic rally in GameStop or Elon Musk sending stocks or cryptocurrencies soaring by firing off the odd tweet. Regardless, there aren't obvious relationships between social media posts and financial prices in the way that arbitrage relationships can guide more conventional quantitative research and analysis in finance. How, when and whether to take cues from social media in a formalized or quantitative framework is still very up in the air. 
## Motivation
The most common use of natural language processing on financial social media is the study of "sentiment", whether the post in question exhibits positive or negative feelings towards the subject in question. This is valuable for marketing and customer relations, but less so for finance, where correlations to prices is the most important thing. Still, sentiment is often used because there are many pre-trained models that can estimate the sentiment of a social media post, and training a new model is often unnecessary. Additionally, prdicting stock data is notoriously difficult, and social media data are notoriously heterogeneous. In order to have any hope of making real progress, it will be necessary to do some pre-processing and filtering.

Here I demonstrate a method for tagging and potentially cleaning social media data based on temporal correlations. In particular, this is a method for detecting "retro-dictive" correlations between stock prices and social media posts: cases where a prior stock movement can be guessed based on the content of a social media post. This could be desirable for a number of different applications, for example if you are interested in trying to use social media posts to predict stock movements it will greatly benefit you to filter out posts that you are confident are _reacting_ to a prior event. 
## Methods
This procedure involves, first and foremost, a dataset of social media posts relating to some financial markets and a related dataset of the history of those markets. In this case I drew the social media posts from Twitter, searching for the past 50 days of twitter history for tweets using the "cashtags" of companies listed in the S&P 100, e.g. tweets containing "$TSLA" for Tesla Motors. I labeled each tweet based on whether the stock increased or decreased on average over the 6 business hours before the tweet occurred, with a 1 for increase and a 0 for decrease. 

Once I have my labeled data, the first thing I do is try to visualize it. To do this I converted the documents to an array embedding using the `doc2vec` model provided by the `gensim` NLP library, and plotted the labeled data with UMAP. Some of the results are shown here:

<figure>
  <img
  src="https://user-images.githubusercontent.com/45473468/139781195-91cb1421-466f-4316-a052-d777d695aad8.png"
  alt="AAPL data">
  <figcaption>Labeled data from Apple</figcaption>
</figure>


<figure>
  <img
  src="https://user-images.githubusercontent.com/45473468/139781522-d3f013e3-7292-4e70-8c24-9c23c6eb7015.png"
  alt="AMZN data">
  <figcaption>Labeled data from Amazon</figcaption>
</figure>


<figure>
  <img
  src="https://user-images.githubusercontent.com/45473468/139781585-b0722a08-7525-4258-a78c-ddd2c62eb48a.png"
  alt="BLK data">
  <figcaption>Labeled data from Blackrock</figcaption>
</figure>


<figure>
  <img
  src="https://user-images.githubusercontent.com/45473468/139781710-86444122-8d41-4c31-ae82-a2b53925dcfe.png"
  alt="MMM data">
  <figcaption>Labeled data from 3M</figcaption>
</figure>

Not surprisingly, the majority of tweets appear to be part of a large cluster with both labels. The majority of tweets presumably do not contain any retrodictive content, especially for very popular stocks such as FAANGs. However, beyond the central cluster there are often some clusters that are primarity one label or the other. These appear to contain retrodictive content, and we can use machine learning to filter them out. 

In order to do this we can use a simple neural network classifier. In the `Retro-diction demonstration` notebook I show this being done for the data from Blackrock. We train the neural network on the labeled document vectors and choose the model with the best performance on the validation data to avoid overfitting and then we can see how well it works as a filter. We can evaluate this by using it to estimate the probability (https://render.githubusercontent.com/render/math?math=p_1(tweet)) that a tweet has a 1 label. We take ![formula](https://render.githubusercontent.com/render/math?math=\frac{1}{4}-p_1(1-p_1)), which reaches its maximum value when the probability is either 1 or 0, and is 0 when the probability is exactly 0.5, and plot it using the same UMAP mapper. This shows which point the filter is very confident in. We can see that this metric matches fairly well with the clusters that are almost uniformly one label or another. Going further, we can then observe the kinds of tweets that the model labeled very confidently. We take the 100 tweets that have the highest labeling confidence and look through them. We can see that it correctly classified some expected tweet types, such as tweets recording recent gains or losses, tweets about earnings reports, etc. It also learned that some people were tweeting about a cryptocurrency called Blink under the same "cashtag" $BLK, and learned that activity related to this cryptocurrency often followed declines in the Blackrock stock price. Whether signal or noise, being able to pick out and identify these patterns in social media data has to potential to be very valuable for financial analytics.
