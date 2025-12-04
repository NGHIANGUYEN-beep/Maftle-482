# Maftle
A wordle game website using the assets from Popular Game "Minecraft"

How to run:
-Run the command "python app.py" in your terminal
If this doesn't work:
-Run "pip install flask" if you don't have it in your environment

Login:
1. Click on "Login", or the bottom leftmost button.

2. If you have not made an account before, click on the words "Create One!" underneath the forms for logging in.
To create an account, you need to enter a username and email that has not been used previously, as well as a password you want to use.
If an email or username has already been chosen, it will return an error and let you know that you need to choose a new email or username.
If all information is determined valid, it will return you back to the Login page.

3. Within the login page, you will now enter the email and password you had decided on in the prior page. Again, if any of this information is entered incorrectly/does  not exist, it will return with an error and have you retype the information.
When the login is successful, it will return you to the homepage and change the "Login" button to a "Logout" button, as well as place a welcome banner on the top right corner.

4. If you wish to logout, just click on the "Logout" button, and it will take you to a page to confirm that you have logged out.
When you click on the button to return to the homepage, the "Login" button will reappear and the top right banner will disappear.

Game:
1. Click infinite or daily mode to access the game, currently there is no difference between the two.
2. Place a stick (the brown rod) in the bottom middle box of the grid by dragging and clicking.
3. Next, place a coal (black blob) in the very middle box of the grid with the same method.
4. Hit submit guess.
5. You should see your past guess on the side of the grid and it will have colors on it to determine if the items you have are for the item you need to craft. If it's red then the item doesn't work for the item you need to guess. If it's green then it's part of the crafting recipe.
6. To make it easier on people that don't know the crafting recipe, the terminal states what the item you need to craft is. Go to recipes.json and find the crafting recipe. This is for testing only and won't be deployed towards the actual game. 
7. After you find the recipe, put in the items for the recipe and submit.
8. If it's correct, you should see the screen become darkened saying you found the correct item, and it will start a new game.