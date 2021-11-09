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
  src="https://user-images.githubusercontent.com/45473468/140551852-a2307e5d-826c-47dc-b662-354d7572d302.png"
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

In order to do this we can use a simple neural network classifier. In the `Retro-diction demonstration` notebook I show this being done for the data from Blackrock. We train the neural network on the labeled document vectors and choose the model with the best performance on the validation data to avoid overfitting and then we can see how well it works as a filter. We can evaluate this by using it to estimate the probability ![formula](https://render.githubusercontent.com/render/math?math=p_1(tweet)) that a tweet has a 1 label. We take ![formula](https://render.githubusercontent.com/render/math?math=\frac{1}{4}-p_1(1-p_1)), which reaches its maximum value when the probability is either 1 or 0, and is 0 when the probability is exactly 0.5, and plot it using the same UMAP mapper. This shows which points the filter is very confident in. 

<figure>
  <img
  src="https://user-images.githubusercontent.com/45473468/140551908-560b9893-51bc-493b-955a-4011edbe2cd0.png"
  alt="BLK data">
  <figcaption>Model confidence in BLK labels</figcaption>
</figure>


We can see that this metric matches fairly well with the clusters that are almost uniformly one label or another. Going further, we can then observe the kinds of tweets that the model labeled very confidently. We take the 100 tweets that have the highest labeling confidence and look through them. We can see that it correctly classified some expected tweet types, such as tweets recording recent gains or losses, tweets about earnings reports, etc. It also learned that some people were tweeting about a cryptocurrency called Blink under the same "cashtag" $BLK, and learned that activity related to this cryptocurrency often followed declines in the Blackrock stock price. Whether signal or noise, being able to pick out and identify these patterns in social media data has to potential to be very valuable for financial analytics.

## Summary and future directions

To put this method in context, it is important to understand how this method differs from the task of predicting price movements. Labeling social media posts based on whether they respond to prior events should properly be considered a data cleaning or data engineering task, since the main function is to be able to mark or remove data that have different types of correlations. For example, if someone is interested in actually performing forecasting based on social media data it will be important to remove posts that are essentially only reactions to past movements since they will be correlated with the price information but in a way that is contrary to the task at hand, and removing them (or a least tagging them) could improve performance. Another potential use is the generation of new datasets: from a marketing, PR, or more broad media analysis perspective it could be very valuable to extract these reactive posts and study them separately to understand which kinds of social reactions to expect given certain kinds of price movements. This information could be very valuable for large institutions such as the Federal Reserve or large banks whose public statements are paid especially close attention by investors all over the world.

All this being said, this is currently at the "proof of concept" stage and there are many directions for potential improvement:
* Dataset size: The foundation of natural language processing is large datasets. The data collection for the project was restricted to the past 60 days due to the `yfinance` package limiting access to intra-day prices to that range. Access to a more complete dataset would be expected to dramatically improve performance and potentially allow the use of more data-intensive high performance models such as transformer-based neural networks such as `BERT` (or its twitter-optimized cousin `BERTweet`). In a similar vein, this project was done with minimal tuning, and performance could potentially be improved by fine tuning the learning procedures as well as the labeling method, which currently just takes into account the sign of the trend from the previous 6 business hours. 
* Improved dataset quality: Social media data is notoriously noisy, and there are many tools from NLP that can be used to generate an improved dataset. Two ways to do this are to engineer the twitter queries and to do post-collection filtering. The former is useful to make sure that a broader range of social media data are available, including tweets that don't use the cashtag (e.g. "$TSLA") and just use the company name. The latter would be useful for mitigating spurious signals in the data, for example certain crypto assets use the same cashtags as some S&P100 companies (as noted above) and this is undesirable. Finally, as noted in the previous point, having a longer span of intraday pricing data would allow an increase in dataset size.
* Key feature identification: An important next step is the work out which features about a company, or asset more broadly, lead to being able to perform this type of retro-diction. We can see that not all companies have clusters that are primarily declining or increasing, Tesla for example appears as a single, essentially homogeneous cluster. We can guess that this may be due to the way that segments of Tesla investors (or executives) use Twitter. One might ask if this is characteristic of tech companies, but find that Apple does in fact show small clusters that are increasing or declining. 
  * I have collected a number of features associated with each ticker that could potentially be useful for this task, such as total market capitalization, total transaction volume, volume of posts both increasing and decreasing, and the cosine similarity of word vectors both within and between labels. There are many data science methods that can help with understanding these differences, such as support vector machines (SVM) to separate companies based on how their social media clusters and methods such as ANOVA to determine which features have the most effect on the data.

Overall I believe this is a novel method that could prove very practical for anyone interested in studying the complicated relationship between social media and market prices. I plan to continue pursuing this as time allows, but will update this only intermittently. If anyone is interested or has any questions I encourage them to reach out to me.
