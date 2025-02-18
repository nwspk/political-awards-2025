Instructions are [here on Google Docs](https://docs.google.com/document/d/1M1C-ya0WQ1eEZpSMYB4ccLGJ8ctHM4kKZhkU0vxxO9Q/edit?tab=t.0#heading=h.yyqjou9klunq)

Update: New frontend to view the newly enriched dataset is [here](https://nwspk.github.io/political-awards-2025/)

You can view previews/summaries of all the projects [here on Streamlit](https://political-tech-awards-2025.streamlit.app/) and find the code for that [here](https://github.com/simonwisdom/political-tech-awards-2025)

Other related documents can be found in [this Google Drive directory](https://drive.google.com/drive/folders/1z8ATKiTcY545uNYLH_mSdopF6UNMH2Q8)

### How to test new algorithms and generate new results

In the scripts dir, see "algorithm_v0.py" - this is a relatively minimalist implementation of a ranking algorithm. Try not to change it! Leave it there as an example.
What you can do though is copy it to a new file, e.g. "algorithm_v1.py" and make whatever changes you want. Each time you submit to the repo, github should automatically run the *newest* file from the scripts dir whose name matches algorithm_*.py, and save the results into the results directory. NB the naming scheme for the results is ${timestamp}_${hash of the commit which triggered the results to be generated}_${algorithm file name which generated the results}.csv


### TODO
- Automate testing that the award column for each generated results csv sums to 5,000,000
- Display results in some nicer way than just csv in github
- Check in the scripts used to generate the source data csv
- Automate generating the source data (incrementally!) when the generation scripts are updated. Maybe a database would be better for this than a csv?
