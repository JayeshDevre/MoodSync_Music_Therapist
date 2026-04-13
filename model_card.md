# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

The most significant weakness is the **single-song genre trap**. Thirteen of the fifteen genres in the catalog appear exactly once. This means a user who prefers rock, jazz, metal, or folk will always get the same song at #1 regardless of how well its numeric features actually match — the +1.0 genre bonus (or +2.0 in the original weights) is unbeatable when there is only one competitor. The system does not discover variety; it just locks onto the one catalog entry that shares a label.

A related problem is the **energy asymmetry bias**. The catalog's mean energy is 0.61, and the energy feature carries the highest numeric weight (×1.5 or ×3.0 in the experiment). Low-energy users (target ≈ 0.30) have only 8 songs within a 0.20 proximity window, while high-energy users (target ≈ 0.85) have 9 — roughly equal coverage. However, because energy is weighted so heavily, a song that is 0.30 off on energy loses up to 0.45–0.90 points depending on the weight setting, which can push genuinely good matches out of the top 5 entirely.

The **binary mood penalty** is another hard edge. Mood is treated as an exact string match — "chill" either equals "chill" or it scores zero. There is no partial credit for moods that are semantically close (relaxed ≈ chill, euphoric ≈ happy, angry ≈ intense). A user who wants "relaxed" music will never get the mood bonus on any song in the catalog, because "relaxed" appears only once. This creates a silent filter bubble: users with less common mood preferences are quietly penalized without any explanation in the output.

Finally, the system has **no diversity enforcement**. The top-k results are always the closest matches, which means a lofi listener will get three lofi songs in a row (the entire lofi section of the catalog) before any cross-genre discovery happens. In a real product this would feel repetitive and would fail to surface songs the user might enjoy but has never considered.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
