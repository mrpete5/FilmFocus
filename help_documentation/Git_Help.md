==================== Git Help Commands ====================

### Improving Commit Messages:
Follow the conventional commits standard:
- Use the present tense ("Add feature" not "Added feature").
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...").
- Limit the first line to 72 characters or less.
- Reference issues and pull requests liberally after the first line.

#### Example:
```plaintext
feat: add search functionality to movie database

- Implement search bar in the header
- Add search results page to display matched movies
- Resolve issue #23


## Common git commands

1. Initialize a new Git repository:
   git init

2. Clone a repository from an existing URL:
   git clone [url]

3. Check the status of changes:
   git status

4. Add changes in a file to the staging area:
   git add [file]

5. Commit the staged changes with a message:
   git commit -m "[message]"

6. View the commit history:
   git log

7. Show differences between the working directory and the index:
   git diff

8. List all local branches:
   git branch

9. Switch to a specific branch:
   git checkout [branch-name]

10. Merge a branch into the current branch:
    git merge [branch-name]

11. List remote repositories connected to the current project:
    git remote

12. Add a remote repository:
    git remote add [name] [url]

13. Push a branch to a remote repository:
    git push [remote-name] [branch-name]

14. Pull the latest changes from the 'dev' branch of the remote repository:
    git pull origin dev

15. Fetch a remote's copy of the current branch:
    git fetch [remote-name]

16. Create a new commit that undoes changes from a previous commit:
    git revert [commit-id]

17. Reset the staging area to the most recent commit:
    git reset

18. Temporarily save changes you don't want to commit immediately:
    git stash
    (To apply the changes later: git stash apply)

===========================================================
