### Submit Answer - step by step
The "submit answer" action is completed in three steps.

- First the user opens the "Submit answer" page which displays a list of all available questions. The questions are retrieved from the Question collection in the MongoDB database and are displayed using bootstrap table, take a look at *templates/submit_answer/question_list.html* to see how it is set up. Bootstrap table has nice automatic search and filtering features. The function that handles the retrieval of the questions *list_question_objects()* can be found in *faceit-concur/db.py*. The main function that handles the whole first step is *show_questions()* which can be found in *faceit-concur/flaskapp.py*. On this "Submit answer" page the user can search and select a question to answer.


- When a question has been selected by the user, the user it taken to a new page, the "Selected question" page, where the multiple choice alternatives and the question image, if available, are displayed. On this page the user can select an answer and submit it. In addition, if the user is of type "Admin" or "Teacher" the correct answer is displayed on the same page. Futhermore a difficulty rating system and a textbox for feedback is available on the page. The function that handles this step is *answer_selected_question()* which is found in *faceit-concur/flaskapp.py*, the corresponding html file is  *templates/submit_answer/selected_question_page.html*


- Finally as the chosen answer has been submitted the user is taken to a confirmation page with some additional information about the answered question. Right now the page displays the average perceived difficulty and a bar plot showing the total amount of answered question by the current user, however this can updated to whatever information is desired. The function that handles this is *show_submission_info()* and can be found in *faceit-concur/flaskapp.py*. The html file that displays the submission info is *templates/submit_answer/answer_submitted_successfully.html*.

The information carried from page to page, such as the selected question id and submitted multiple choice answer is passed using json dictionaries. This is done using the *Flask.redirect()*, in the code the information is stored in the *messages[]* dictionary. See *show_questions()* and *answer_selected_question()*, found in *faceit-concur/flaskapp.py*, to how it is done.

### Image in cache to html

To display an image in html without having to store it locally on the server one can save the image in cache as a byte64 string and send it directly to HTML page.
This method can be used both to retrieve and display images from the MongoDB database as well as creating and displaying custom plots. The encoding/decoding examples can be found in functions *get_question_image(question_id)* and *make_bar_plot(question_data)* both in the *faceit-concur/db.py* file.

[Back to main README](https://github.com/damianovar/faceit-concur)
