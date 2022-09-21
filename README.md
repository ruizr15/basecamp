# Basecamp

Basecamp is HackGSU's 2020 StateFarm Competition First Place Winner out of over 200 competitors. 

### What is it?

Basecamp is a camping trip planning tool that helps you find where to go and what to bring on your campout. Basecamp automatically suggests what to bring based on the weather, activities, and more for hundreds of campsites accross the US. 

### How does it work?

Basecamp is made in the Python Flask framework and uses data from the National Parks Service API to provide campgrounds, activities, descriptions, and pictures of the parks. We then use the address of that park and google maps api to get the latitude and longitude before finally using the weather.gov api to get the most accurate weather forecast available. Based on this, the website will recommend weather appropriate packing suggestions.

### Why did we do it?

The StateFarm category was to make a project that "Helps make life go right". Prior to this competition, we were planning a camping trip of our own. We noticed that in that process we had to use multiple websites to get the information we needed, and that it was easy to forget things in this process. Most of us being Eagle Scouts with heavy camping experience, we are all to familiar with the difference that forgetting a rain jacket can make on a campout. So, we created Basecamp, where all the information we needed was in one spot to make campouts go right.
