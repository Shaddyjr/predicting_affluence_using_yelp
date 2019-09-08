# Predicting Areas of Affluence using Yelp Pricing Data
#### Authors: 
- Eddie Yip  [GitHub](https://github.com/Tempyst) | [Medium](https://medium.com/@eddie.yip2) | [LinkedIn](https://www.linkedin.com/in/eddie-yip-2a37324b/)
- Hadi Morrow [GitHub](https://github.com/HadiMorrow) | [Medium](https://medium.com/@hadi.a.morrow) | [LinkedIn](https://www.linkedin.com/in/hadi-morrow-4b94164b/)
- Mahdi Shadkam-Farrokhi: [GitHub](https://github.com/Shaddyjr) | [Medium](https://medium.com/@mahdis.pw) | [LinkedIn](https://www.linkedin.com/in/mahdi-shadkam-farrokhi-m-s-8a410958/) | [mahdis.pw](http://mahdis.pw)

## Problem Statement

In recent years, natural disasters have become an increasingly prevalent concern. In 2017, Hurricane Maria killed almost 6,000 in Puerto Rico with over $90 billion in damages. Hurricane Irma also hit Puerto Rico and southern parts of the US killing over 100 with over $60 billion in damages. Wildfires, hurricanes, and floods have become an all too common occurance in the US - [source](https://en.wikipedia.org/wiki/List_of_natural_disasters_in_the_United_States).

In these disaster situations, first responders have the difficult task of deciding where to send initial precious resources. Our client, New Light Technologies, is concerned with utilizing novel data sources as a practical solution to help first responders with these kinds of decisions. In particular, can Yelp "$" price data be used to determine the affluence of an area? It is assumed an area's affluence can serve as a marker for disaster-resistance, whereas an area with low affluence have the greatest need. If a reasonable correlation can be found, first responders would be able to quickly assess which areas need relief the most and act accordingly - [source 1](https://www.scientificamerican.com/article/natural-disasters-by-location-rich-leave-and-poor-get-poorer/ ) + [source 2](http://communitystudies.qwriting.qc.cuny.edu/2011/11/09/income-distribution/).

By pulling Yelp data from the Yelp API and matching business location zip codes to IRS data, we determine whether Yelp "$" price data correlates with affluence using various supervised learning models. We will restrict our locations to New York City, since it has faced a number of natural disasters and is an area we have subject knowledge in. Also, we will use specificity as our metric for model selection.

## Relevant Files
- [Data Gathering Resource](yelp_data_gather.ipynb)
- [Main NoteBook](code/client_project_notebook.ipynb)
- [Graphs and Visuals](images)
- [File Data](data)

## Executive Summary 

At the start of this project, our team had some naive assumptions about how strongly the Yelp "$" price of a business correlated to the affluency of the area it was in. Namely, we assumed the higher the Yelp price, the higher the affluence. And this is where we first encountered the issue of how we were going to define "affluence".

In our definition of "affluence", we needed to be objective and systematic. After some research, we settled on IRS tax return data. These data showed the tax returns by zip code along with the income brackets for those returns. By looking through each zip code and calculating the proportion of individuals in the highest bracket, we had our "affluency rate". We simply needed to settle on an arbitrary threshold, which we determined through research and subjective selection.

We also debated on which Yelp dataset to use, of which there were two - a large given dataset and the Yelp API. The given dataset was massive but included areas from all over the US with the vast majority being from Arizona. The Yelp API offered us the flexibility to select the locations we wanted to pull data for. Also, these data would be immediately up to date. For these reasons, we settled on using the Yelp API. Regarding location, New York City (NYC) experienced 25% of all the worst, or super severe, disasters occurring in the US from 1930 to 2010, which makes is a priority target for this problem. We also agreed to focus on NYC since each team member was already familiar with NYC and could bring subject knowledge to bear during the process. 
We believed we could use NYC to successfully show a proof of concept for our model.

While modeling, we ran into some issues. First, we had longitude and latitude data for businesses, and we wanted to use them inform our model, but by themselves longitude and latitude were not significant factors. We ended up clustering longitude and latitude to create a new feature, which succinctly summarized the general location of each observation. We also ended up with almost 300 features, to which we had relatively few total observations. Although not a large concern, we decided to explore models using all the variables and, separately, a restricted number of features showing the highest correlation with our target. Lastly, we initially used accuracy as our model metric, but quickly discovered this was not ideal given the problem, which involves emergency response. Our use-case involves potentially sending vital resources to those in the most need - as such we wanted to focus on reducing false negatives and settled on specificity as our main metric.

In all, we set out to discover how related the Yelp "$" price is to affluency and we effectively achieved this goal. It was also interesting to discover how significant review ratings and location played in predicting affluency.


## Conclusion:
We set out to use Yelp "$" price to determine the affluency of neighborhoods and our findings show the Yelp $ price plays a small, if not insignificant role, in predicting neighborhood affluency.

By far, location was found to be the best determinate for affluency. Also, the sheer number of Yelp comments was another significant determinant. We found this odd, as one would expect review quality to be a better indicator. We suspect the number of Yelp comments is correlating with another factor - foot traffic around commercial areas. It's plausible the businesses in commercial areas have substantially high foot traffic, leading to a high number of Yelp comments.

There were several problems with predicting affluency using these data. Firstly, some data were not well represented. The data was heavily skewed towards 1 "$" and 2 "$$" prices, which did not allow for a fair representation of all prices. Also, some zip codes are physically larger than others causing small zip codes to over-represent businesses observed in their area.

Also, the IRS data we used only factors in resident citizens and not businesses. This led to several NYC zip code not appearing in the IRS dataset at all. For example, we could not find 10020, a small zip code encompassing the affluent Rockefeller Center. It was not possible to know the true affluency for these missing areas without subject knowledge. This led to some commercial districts skewing our results, since these neighborhoods tend to be affluent, but were misclassified by our model.

It is important to note that despite the false negative misclassification, our model would still effectively steer resources to these needy areas, as they tend to have a high population density.

In the case of an emergency, our query function proves to be a good predictor for where emergency resources should be sent first. Of course, this model only applies to NYC, but shows a proof of concept that could be applicable for other areas.

While working through this problem, we made the following assumptions:
- An area's affluence can serve as a marker for disaster-resistance
- We arbitrarily set an affluency threshold of 15%
- $200,000+ income was the cutoff used to determine the affluency rate for a zip code
- New York City is a representative area for the problem
- A correlation of 2% was used as the cutoff for reducing features, which reduced the number of features by 30%
- We assumed specificity was the best metric

## Recommendations:
We recommend that emergency services prioritize sending resources to areas with low affluency and high population density. For NYC, our `query` model can be used for this purpose.

For future work, we would be interested in creating a similar model for other locations to test the portability of our process.

Additionally, we would recommend Yelp add an indicator (in their API) to flag if a business is in a commercial area.


## Source Documentation

- [NYC zip codes](https://www.nycbynatives.com/nyc_info/new_york_city_zip_codes.php)
- [Yelp API - Business Endpoints](https://www.yelp.com/fusion)
- [IRS dataset](https://www.irs.gov/statistics/soi-tax-stats-individual-income-tax-statistics-2016-zip-code-data-soi)