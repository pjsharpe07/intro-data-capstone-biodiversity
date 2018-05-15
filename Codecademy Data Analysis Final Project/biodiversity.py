
# coding: utf-8

# # Capstone 2: Biodiversity Project

# # Introduction
# You are a biodiversity analyst working for the National Parks Service.  You're going to help them analyze some data about species at various national parks.
# 
# Note: The data that you'll be working with for this project is *inspired* by real data, but is mostly fictional.

# # Step 1
# Import the modules that you'll be using in this assignment:
# - `from matplotlib import pyplot as plt`
# - `import pandas as pd`

# In[2]:


from matplotlib import pyplot as plt
import pandas as pd


# # Step 2
# You have been given two CSV files. `species_info.csv` with data about different species in our National Parks, including:
# - The scientific name of each species
# - The common names of each species
# - The species conservation status
# 
# Load the dataset and inspect it:
# - Load `species_info.csv` into a DataFrame called `species`

# In[3]:


species = pd.read_csv('species_info.csv')


# In[4]:


species.head()


# # Step 3
# Let's start by learning a bit more about our data.  Answer each of the following questions.

# In[5]:


unique_species = species.scientific_name.nunique()
print(unique_species)


# In[6]:


unique_categories = species.category.unique()
print(unique_categories)


# In[7]:


unique_conservation_status = species.conservation_status.unique()
print(unique_conservation_status)


# # Step 4
# Let's start doing some analysis!
# 
# The column `conservation_status` has several possible values:
# - `Species of Concern`: declining or appear to be in need of conservation
# - `Threatened`: vulnerable to endangerment in the near future
# - `Endangered`: seriously at risk of extinction
# - `In Recovery`: formerly `Endangered`, but currnetly neither in danger of extinction throughout all or a significant portion of its range
# 
# We'd like to count up how many species meet each of these criteria.  Use `groupby` to count how many `scientific_name` meet each of these criteria.

# In[8]:


status_count = species.groupby('conservation_status').scientific_name.nunique()
status_count


# In[9]:


species.fillna('No Intervention', inplace=True)


# In[10]:


species.groupby('conservation_status').scientific_name.nunique().reset_index()


# In[12]:


protection_counts = species.groupby('conservation_status').scientific_name.nunique().reset_index().sort_values(by='scientific_name')
protection_counts


# In[13]:


plt.figure(figsize=(10, 4))
ax = plt.subplot()
plt.bar(range(len(protection_counts['conservation_status'])) ,protection_counts['scientific_name'])

ax.set_xticks(range(len(protection_counts['conservation_status'])))
ax.set_xticklabels(protection_counts['conservation_status'])
plt.ylabel('Number of Species')
plt.title('Conservation Status by Species')
plt.show()


# Now let's take a closer look at the breakdown of only protected species by category.

# In[14]:


only_protected = protection_counts.drop([2])
only_protected


# In[15]:


plt.figure(figsize=(10,4))
plt.pie(only_protected.scientific_name, labels=only_protected.conservation_status, autopct = '%0.1f% %')
plt.axis('equal')
plt.title('Protected Species by Category')
plt.show()


# # Step 4
# Are certain types of species more likely to be endangered?

# In[16]:


species['is_protected'] = species.conservation_status != 'No Intervention'


# In[17]:


category_counts = species.groupby(['category', 'is_protected']).scientific_name.nunique().reset_index()


# In[18]:


category_counts


# In[19]:


category_pivot = category_counts.pivot(columns='is_protected',
                               index='category',
                               values='scientific_name').reset_index()


# In[20]:


category_pivot


# In[21]:


category_pivot.columns = ['category','not_protected', 'protected']
category_pivot


# In[22]:


#calculates total species
category_pivot['total_species'] = category_pivot['not_protected'] + category_pivot['protected']
#calculates the percent that are protected
category_pivot['percent_protected'] = category_pivot['protected'] / category_pivot['total_species']


# In[23]:


category_pivot


# It appears that there's a much higher percent for `mammals` and `birds` than there are for `reptiles`. Let's see if there's any significance here.

# In[26]:


#for mammals and birds
contingency = [[category_pivot['protected'].iloc[3], category_pivot['not_protected'].iloc[3]],
               [category_pivot['protected'].iloc[1], category_pivot['not_protected'].iloc[1]]
              ]

contingency


# In[27]:


from scipy.stats import chi2_contingency


# In[75]:


chi2, pval, dof, expected = chi2_contingency(contingency)
print(pval)


# This p-value is too high for us to make any conclusions about `mammals` and `birds`. Let's try another pair: `reptiles` and `mammals`

# In[76]:


#for reptiles and mammals
contingency2 = [[category_pivot['protected'].iloc[3], category_pivot['not_protected'].iloc[3]],
               [category_pivot['protected'].iloc[5], category_pivot['not_protected'].iloc[5]]
              ]

chi_rep, pval_rep, dof_rep, expected_rep = chi2_contingency(contingency2)
print(pval_rep)


# Yes! It looks like there is a significant difference between `Reptile` and `Mammal`!

# # Step 5

# Conservationists have been recording sightings of different species at several national parks for the past 7 days.  They've sent you their observations in a file called `observations.csv`.  Load `observations.csv` into a variable called `observations`, then use `head` to view the data.

# In[29]:


observations = pd.read_csv('observations.csv')
observations.head()


# Some scientists are studying the number of sheep sightings at different national parks.  There are several different scientific names for different types of sheep.  We'd like to know which rows of `species` are referring to sheep.  Notice that the following code will tell us whether or not a word occurs in a string:

# First I'll make a new column to decide if the record is a `Sheep`.

# In[30]:


species['is_sheep'] = species.apply(lambda row: True if 'Sheep' in row['common_names'] else False, axis=1)
species.head()


# Let's only look at `Sheep` species.

# In[31]:


sheep_df = species[species.is_sheep == True]
sheep_df.head(15)


# Many of the results are actually plants. Let's only select rows of `species` where `category` is `Mammal`.

# In[32]:


sheep_species = species[(species.is_sheep) & (species.category == 'Mammal')]
sheep_species.head()


# Let's combine `sheep_species` with `observations` to get a DataFrame with observations of sheep.

# In[33]:


sheep_observations = pd.merge(observations, sheep_species)
sheep_observations


# Let's take a look at the observations at each park over the last 7 days.

# In[34]:


obs_by_park = sheep_observations.groupby('park_name').observations.sum().reset_index().sort_values(by='observations')
obs_by_park


# Let's see what this looks like visually by creating a bar chart.

# In[35]:


plt.figure(figsize=(16, 4))
ax2 = plt.subplot()
plt.bar(range(len(obs_by_park['park_name'])), obs_by_park['observations'])
ax2.set_xticks(range(len(obs_by_park['park_name'])))
ax2.set_xticklabels(obs_by_park['park_name'])
plt.ylabel('Number of Observations')
plt.title('Observations of Sheep per Week')
plt.show()


# Our scientists know that 15% of sheep at Bryce National Park have foot and mouth disease.  Park rangers at Yellowstone National Park have been running a program to reduce the rate of foot and mouth disease at that park.  The scientists want to test whether or not this program is working.  They want to be able to detect reductions of at least 5 percentage point.  For instance, if 10% of sheep in Yellowstone have foot and mouth disease, they'd like to be able to know this, with confidence.
# 
# Use the sample size calculator at <a href="https://www.optimizely.com/sample-size-calculator/">Optimizely</a> to calculate the number of sheep that they would need to observe from each park.  Use the default level of significance (90%).
# 
# Remember that "Minimum Detectable Effect" is a percent of the baseline.

# In[36]:


minimum_detectable_effect = (.05 / .15) * 100
baseline = 15
stat_sig =0.90

minimum_detectable_effect


# In[37]:


sample_size = 510


# How many weeks would you need to observe sheep at Bryce National Park in order to observe enough sheep?  How many weeks would you need to observe at Yellowstone National Park to observe enough sheep?

# In[38]:


obs_at_bryce = 510 / 250
obs_at_yellowstone = 510 / 507
obs_at_bryce, obs_at_yellowstone


# So you will need about 2 weeks at Bryce National Park and about 1 week at Yellowstone.
