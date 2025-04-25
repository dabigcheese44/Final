document.addEventListener('DOMContentLoaded', function () {
    const addEmailButton = document.getElementById('add-email-button');
    const memberEmailsContainer = document.getElementById('member-emails-container');
    const createBoardForm = document.getElementById('create-board-form');
    const boardsList = document.getElementById('boards-list');
    const noBoardsMessage = document.getElementById('no-boards-message');

    // Function to Add an Email Input
    function addEmailField() {
        const emailEntry = document.createElement('div');
        emailEntry.classList.add('email-entry');

        const emailInput = document.createElement('input');
        emailInput.type = 'email';
        emailInput.placeholder = 'Enter member email';
        emailInput.classList.add('email-input');
        emailInput.required = true;

        const removeButton = document.createElement('button');
        removeButton.type = 'button';
        removeButton.textContent = 'Remove';
        removeButton.classList.add('remove-email-button');

        removeButton.addEventListener('click', function () {
            emailEntry.remove();
        });

        emailEntry.appendChild(emailInput);
        emailEntry.appendChild(removeButton);
        memberEmailsContainer.appendChild(emailEntry);
    }

    // Attach click event to Add Email Button
    addEmailButton.addEventListener('click', addEmailField);

    // Function to Add a Board to the Existing Boards List
    function addBoardToExistingBoards(boardId, boardName) {
        if (noBoardsMessage) {
            noBoardsMessage.style.display = 'none'; // Hide "no boards" message
        }

        const boardItem = document.createElement('li');
        boardItem.classList.add('board-item');
        boardItem.textContent = boardName;
        boardItem.addEventListener('click', function () {
            window.location.href = `/home?board_id=${boardId}`;
        });

        boardsList.appendChild(boardItem);
    }

    // Handle Form Submission
    createBoardForm.addEventListener('submit', function (event) {
        event.preventDefault();

        const boardNameInput = document.getElementById('board-name');
        const boardName = boardNameInput.value;

        const emailInputs = document.querySelectorAll('.email-input');
        const memberEmails = Array.from(emailInputs).map(input => input.value);

        const formData = new FormData();
        formData.append('board-name', boardName);
        memberEmails.forEach(email => formData.append('member-emails[]', email));

        fetch('/processcreateboard', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Add the new board to the existing boards list
                addBoardToExistingBoards(data.board_id, data.board_name);

                // Redirect to the new board's home page
                window.location.href = data.redirect;
            } else {
                alert(data.message || 'An error occurred while creating the board.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while processing your request.');
        });
    });
});
