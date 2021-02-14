# flashcard

Flashcard WebApp for my kids to practice before taking XtraMath progress quizzes
* Supports all the operations (+, -, x, /)
* flexible to add your own specific problems to practice through a file and while running. 

It's not perfect -- but my kids are getting better at math so... yah

Example Running 25 Multiplication Questions, 10 second timer, and repeat right away if you miss

```bash
virtualenv -p python3 venv
. venv/bin/activate
pip install -r requirements.txt
python -m flashcard -N 25 -i practice.txt -w 10 -o x --repeat next
```
