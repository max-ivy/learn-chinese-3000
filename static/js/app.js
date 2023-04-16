$(document).ready(function() {

    // get random card from database
    function getRandomCard() {
      $.ajax({
        url: "/get_random_card",
        type: "GET",
        success: function(data) {
          console.log(data);
          displayCard(data);
        },
        error: function() {
          console.log("Error getting random card");
        }
      });
    }
    function handleArrowKeyPress(event) {
        const UP_ARROW_KEY = 38;
        const LEFT_ARROW_KEY = 37;
        const RIGHT_ARROW_KEY = 39;
      
        // Check which arrow key is pressed
        if (event.which === UP_ARROW_KEY) {
          // If the up arrow key is pressed, trigger a click event on the flip button
          $("#flip-button").click();
        } else if (event.which === LEFT_ARROW_KEY) {
          // If the left arrow key is pressed, call the function to show the previous card
          getPrevCard();
        } else if (event.which === RIGHT_ARROW_KEY) {
          // If the right arrow key is pressed, call the function to show the next card
          getNextCard();
        }
      }
      

    // Add the event listener for keydown event
  $(document).keydown(function(event) {
    handleArrowKeyPress(event);
  });

  
    // display card on front of flashcard
    function displayCard(card) {
        if (card != null) {
            var isFlipped = $("#flashcard-container").hasClass("flip");
            if (isFlipped) {
                $("#word").text(card.word_back).attr("data-card-id", card._id);
                $("#translation").text(card.translation_back);
                $("#pinyin").text(card.pinyin_back);
                $("#type").text(card.type_back);
                $("#category").text(card.category_back);
            } else {
                $("#word").text(card.word).attr("data-card-id", card._id);
                $("#translation").text(card.translation);
                $("#pinyin").text(card.pinyin);
                $("#type").text(card.type);
                $("#category").text(card.category);
            }
        }
    }
    
      
      
      
    // flip card to reveal back
    function flipCard() {
        var currentCardId = $("#word").attr("data-card-id");
        $.ajax({
            url: "/get_card_back",
            type: "GET",
            data: { current_card_id: currentCardId },
            success: function(data) {
                console.log(data);
                $("#word").text(data.word_back);
                $("#translation").text(data.translation_back);
                $("#pinyin").text(data.pinyin_back);
                $("#type").text(data.type_back);
                $("#category").text(data.category_back);
            },
            error: function() {
                console.log("Error getting card back");
            }
        });
        $("#flashcard-front").hide();
        $("#flashcard-back").show();
    }
    
    
      
  
    // flip card to reveal front
    function unflipCard() {
      $("#flashcard-front").show();
      $("#flashcard-back").hide();
    }
  
    // get next card in database
    function getNextCard() {
        var currentCardId = $("#word").attr("data-card-id");
        $.ajax({
            url: "/get_next_card",
            type: "GET",
            data: { 
                current_card_id: currentCardId,
                randomize: isRandomizeChecked()
            },
            success: function(data) {
                console.log(data);
                displayCard(data);
            },
            error: function() {
                console.log("Error getting next card");
            }
        });
    }
    
    function getPrevCard() {
        var currentCardId = $("#word").attr("data-card-id");
        $.ajax({
            url: "/get_prev_card",
            type: "GET",
            data: { 
                current_card_id: currentCardId,
                randomize: isRandomizeChecked()
            },
            success: function(data) {
                console.log(data);
                displayCard(data);
            },
            error: function() {
                console.log("Error getting previous card");
            }
        });
    }
    
  
    // bind click handlers to buttons
    $("#flip-button").click(function() {
        $("#flashcard").toggleClass("flip");
    });
    
  
    $("#next-button").click(function() {
      getNextCard();
    });
  
    $("#prev-button").click(function() {
      getPrevCard();
    });
  
// randomize cards
$("#randomize").change(function() {
    var isChecked = $(this).is(":checked");
    $.ajax({
      url: "/set_randomize",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify({ randomize: isChecked }),
      success: function(data) {
        console.log(data);
      },
      error: function() {
        console.log("Error setting randomize");
      }
    });
  });

  // initialize page
  getRandomCard();

  function isRandomizeChecked() {
      return $("#randomize").is(":checked");
  }
  

});

// function to load all cards into the table
function loadCards() {
  // Make a request to the server to get all cards from the database
  // Replace the URL with the appropriate route in your app.py
  $.getJSON('/get_all_cards', function(data) {
    let tableBody = $('#cards-table tbody');
    tableBody.empty();

    data.forEach(function(card) {
      console.log(card.word, card.translation, card.pinyin, card.type, card.category); // Add this line
      let row = $('<tr></tr>');
      row.append(`<td>${card.word}</td>`);
      row.append(`<td>${card.translation}</td>`);
      row.append(`<td>${card.pinyin}</td>`);
      row.append(`<td>${card.type}</td>`);
      row.append(`<td>${card.category}</td>`);
      row.append(`<td><button class="delete-card" data-id="${card._id}">Delete</button></td>`);
      tableBody.append(row);
    });
  });
}

// Load cards on page load
loadCards();

// Handle the form submit event
$('#add-card-form').submit(function(event) {
  event.preventDefault();

  const requestData = {
    word_input: $('#word-input').val(),
    translation_input: $('#translation-input').val(),
    pinyin_input: $('#pinyin-input').val(),
    type_input: $('#type-input').val(),
    category_input: $('#category-input').val(),
  };
  

  console.log('Form inputs:', requestData);

  // check if any of the input fields are empty
  if (!requestData.word_input || !requestData.translation_input || !requestData.pinyin_input || !requestData.type_input || !requestData.category_input) {
      console.log('Please fill in all fields');
      return;
  }

  // Make a request to the server to add the new card
  $.ajax({
    url: '/add_card',
    method: 'POST',
    contentType: 'application/json',
    data: JSON.stringify(requestData),
    success: function() {
      console.log('New card added successfully');
      // Clear the form
      $('#add-card-form').trigger('reset');
      // Reload the cards in the table
      loadCards();
    },
    error: function() {
      console.log("Error adding new card");
    },
  });
});

// Handle the delete button click for each card
$('#cards-table tbody').on('click', '.delete-card', function() {
  let cardId = $(this).data('id');
  
  // Make a request to the server to delete the card
  $.ajax({
      url: `/delete_card/${cardId}`,
      method: 'DELETE',
      success: function() {
          console.log('Card deleted successfully');
          // Reload the cards in the table
          loadCards();
      },
      error: function() {
          console.log("Error deleting card");
      },
  });
});
 
document.getElementById('csv-upload-form').addEventListener('submit', async (event) => {
    event.preventDefault();
  
    const formData = new FormData();
    formData.append('csv-file', document.getElementById('csv-file').files[0]);
  
    try {
      const response = await fetch('/upload-csv', {
        method: 'POST',
        body: formData,
      });
  
      if (response.ok) {
        // Reset the form after a successful upload
        event.target.reset();
        // Refresh the data in the app
      } else {
        throw new Error('Error uploading CSV');
      }
    } catch (error) {
      console.error('Error uploading CSV:', error);
    }
  });
  
