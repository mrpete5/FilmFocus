$(document).ready(function () {
	"use strict"; // start of use strict

	/*==============================
	Menu
	==============================*/
	$('.header__btn').on('click', function() {
		$(this).toggleClass('header__btn--active');
		$('.header__nav').toggleClass('header__nav--active');
		$('.body').toggleClass('body--active');

		if ($('.header__search-btn').hasClass('active')) {
			$('.header__search-btn').toggleClass('active');
			$('.header__search').toggleClass('header__search--active');
		}
	});

	/*==============================
	Search
	==============================*/
	$('.header__search-btn').on('click', function() {
		$(this).toggleClass('active');
		$('.header__search').toggleClass('header__search--active');

		if ($('.header__btn').hasClass('header__btn--active')) {
			$('.header__btn').toggleClass('header__btn--active');
			$('.header__nav').toggleClass('header__nav--active');
			$('.body').toggleClass('body--active');
		}
	});

	/*==============================
	Home
	==============================*/
	$('.home__bg').owlCarousel({
		animateOut: 'fadeOut',
		animateIn: 'fadeIn',
		mouseDrag: false,
		touchDrag: false,
		items: 1,
		dots: false,
		loop: true,
		autoplay: false,
		smartSpeed: 600,
		margin: 0,
	});

	$('.home__bg .item').each( function() {
		if ($(this).attr("data-bg")){
			$(this).css({
				'background': 'url(' + $(this).data('bg') + ')',
				'background-position': 'center center',
				'background-repeat': 'no-repeat',
				'background-size': 'cover'
			});
		}
	});

	$('.home__carousel').owlCarousel({
		mouseDrag: false,
		touchDrag: false,
		dots: false,
		loop: true,
		autoplay: false,
		smartSpeed: 600,
		margin: 30,
		responsive : {
			0 : {
				items: 2,
			},
			576 : {
				items: 2,
			},
			768 : {
				items: 3,
			},
			992 : {
				items: 4,
			},
			1200 : {
				items: 4,
			},
		}
	});

	$('.home__nav--next').on('click', function() {
		$('.home__carousel, .home__bg').trigger('next.owl.carousel');
	});
	$('.home__nav--prev').on('click', function() {
		$('.home__carousel, .home__bg').trigger('prev.owl.carousel');
	});

	$(window).on('resize', function() {
		var itemHeight = $('.home__bg').height();
		$('.home__bg .item').css("height", itemHeight + "px");
	});
	$(window).trigger('resize');

	/*==============================
	Tabs
	==============================*/
	$('.content__mobile-tabs-menu li').each( function() {
		$(this).attr('data-value', $(this).text().toLowerCase());
	});

	$('.content__mobile-tabs-menu li').on('click', function() {
		var text = $(this).text();
		var item = $(this);
		var id = item.closest('.content__mobile-tabs').attr('id');
		$('#'+id).find('.content__mobile-tabs-btn input').val(text);
	});

	/*==============================
	Section bg
	==============================*/
	$('.section--bg, .details__bg').each( function() {
		if ($(this).attr("data-bg")){
			$(this).css({
				'background': 'url(' + $(this).data('bg') + ')',
				'background-position': 'center center',
				'background-repeat': 'no-repeat',
				'background-size': 'cover'
			});
		}
	});

	/*==============================
	Filter
	==============================*/
	$('.filter__item-menu li').each( function() {
		$(this).attr('data-value', $(this).text().toLowerCase());
	});

	$('.filter__item-menu li').on('click', function() {
		var text = $(this).text();
		var item = $(this);
		var id = item.closest('.filter__item').attr('id');
		$('#'+id).find('.filter__item-btn input').val(text);
	});

	/*==============================
	Scroll bar
	==============================*/
	$('.scrollbar-dropdown').mCustomScrollbar({
		axis: "y",
		scrollbarPosition: "outside",
		theme: "custom-bar"
	});

	$('.accordion').mCustomScrollbar({
		axis: "y",
		scrollbarPosition: "outside",
		theme: "custom-bar2"
	});

	/*==============================
	Morelines
	==============================*/
	$('.card__description--details').moreLines({
		linecount: 6,
		baseclass: 'b-description',
		basejsclass: 'js-description',
		classspecific: '_readmore',
		buttontxtmore: "",
		buttontxtless: "",
		animationspeed: 400
	});

	/*==============================
	Gallery
	==============================*/
	var initPhotoSwipeFromDOM = function(gallerySelector) {
		// parse slide data (url, title, size ...) from DOM elements 
		// (children of gallerySelector)
		var parseThumbnailElements = function(el) {
			var thumbElements = el.childNodes,
				numNodes = thumbElements.length,
				items = [],
				figureEl,
				linkEl,
				size,
				item;

			for(var i = 0; i < numNodes; i++) {

				figureEl = thumbElements[i]; // <figure> element

				// include only element nodes 
				if(figureEl.nodeType !== 1) {
					continue;
				}

				linkEl = figureEl.children[0]; // <a> element

				size = linkEl.getAttribute('data-size').split('x');

				// create slide object
				item = {
					src: linkEl.getAttribute('href'),
					w: parseInt(size[0], 10),
					h: parseInt(size[1], 10)
				};

				if(figureEl.children.length > 1) {
					// <figcaption> content
					item.title = figureEl.children[1].innerHTML; 
				}

				if(linkEl.children.length > 0) {
					// <img> thumbnail element, retrieving thumbnail url
					item.msrc = linkEl.children[0].getAttribute('src');
				} 

				item.el = figureEl; // save link to element for getThumbBoundsFn
				items.push(item);
			}

			return items;
		};

		// find nearest parent element
		var closest = function closest(el, fn) {
			return el && ( fn(el) ? el : closest(el.parentNode, fn) );
		};

		// triggers when user clicks on thumbnail
		var onThumbnailsClick = function(e) {
			e = e || window.event;
			e.preventDefault ? e.preventDefault() : e.returnValue = false;

			var eTarget = e.target || e.srcElement;

			// find root element of slide
			var clickedListItem = closest(eTarget, function(el) {
				return (el.tagName && el.tagName.toUpperCase() === 'FIGURE');
			});

			if(!clickedListItem) {
				return;
			}

			// find index of clicked item by looping through all child nodes
			// alternatively, you may define index via data- attribute
			var clickedGallery = clickedListItem.parentNode,
				childNodes = clickedListItem.parentNode.childNodes,
				numChildNodes = childNodes.length,
				nodeIndex = 0,
				index;

			for (var i = 0; i < numChildNodes; i++) {
				if(childNodes[i].nodeType !== 1) { 
					continue; 
				}

				if(childNodes[i] === clickedListItem) {
					index = nodeIndex;
					break;
				}
				nodeIndex++;
			}

			if(index >= 0) {
				// open PhotoSwipe if valid index found
				openPhotoSwipe( index, clickedGallery );
			}
			return false;
		};

		// parse picture index and gallery index from URL (#&pid=1&gid=2)
		var photoswipeParseHash = function() {
			var hash = window.location.hash.substring(1),
			params = {};

			if(hash.length < 5) {
				return params;
			}

			var vars = hash.split('&');
			for (var i = 0; i < vars.length; i++) {
				if(!vars[i]) {
					continue;
				}
				var pair = vars[i].split('=');  
				if(pair.length < 2) {
					continue;
				}           
				params[pair[0]] = pair[1];
			}

			if(params.gid) {
				params.gid = parseInt(params.gid, 10);
			}

			return params;
		};

		var openPhotoSwipe = function(index, galleryElement, disableAnimation, fromURL) {
			var pswpElement = document.querySelectorAll('.pswp')[0],
				gallery,
				options,
				items;

			items = parseThumbnailElements(galleryElement);

			// define options (if needed)
			options = {

				// define gallery index (for URL)
				galleryUID: galleryElement.getAttribute('data-pswp-uid'),

				getThumbBoundsFn: function(index) {
					// See Options -> getThumbBoundsFn section of documentation for more info
					var thumbnail = items[index].el.getElementsByTagName('img')[0], // find thumbnail
						pageYScroll = window.pageYOffset || document.documentElement.scrollTop,
						rect = thumbnail.getBoundingClientRect(); 

					return {x:rect.left, y:rect.top + pageYScroll, w:rect.width};
				}

			};

			// PhotoSwipe opened from URL
			if(fromURL) {
				if(options.galleryPIDs) {
					// parse real index when custom PIDs are used 
					// http://photoswipe.com/documentation/faq.html#custom-pid-in-url
					for(var j = 0; j < items.length; j++) {
						if(items[j].pid == index) {
							options.index = j;
							break;
						}
					}
				} else {
					// in URL indexes start from 1
					options.index = parseInt(index, 10) - 1;
				}
			} else {
				options.index = parseInt(index, 10);
			}

			// exit if index not found
			if( isNaN(options.index) ) {
				return;
			}

			if(disableAnimation) {
				options.showAnimationDuration = 0;
			}

			// Pass data to PhotoSwipe and initialize it
			gallery = new PhotoSwipe( pswpElement, PhotoSwipeUI_Default, items, options);
			gallery.init();
		};

		// loop through all gallery elements and bind events
		var galleryElements = document.querySelectorAll( gallerySelector );

		for(var i = 0, l = galleryElements.length; i < l; i++) {
			galleryElements[i].setAttribute('data-pswp-uid', i+1);
			galleryElements[i].onclick = onThumbnailsClick;
		}

		// Parse URL and open gallery if it contains #&pid=3&gid=1
		var hashData = photoswipeParseHash();
		if(hashData.pid && hashData.gid) {
			openPhotoSwipe( hashData.pid ,  galleryElements[ hashData.gid - 1 ], true, true );
		}
	};
	// execute above function
	initPhotoSwipeFromDOM('.gallery');

	/*==============================
	Player
	==============================*/
	function initializePlayer() {
		if ($('#player').length) {
			const player = new Plyr('#player');
		} else {
			return false;
		}
		return false;
	}
	$(window).on('load', initializePlayer());

	/*==============================
	Range sliders
	==============================*/
	/*1*/
	function initializeFirstSlider() {
		if ($('#filter__years').length) {
			var firstSlider = document.getElementById('filter__years');
			noUiSlider.create(firstSlider, {
				range: {
					'min': 2000,
					'max': 2018
				},
				step: 1,
				connect: true,
				start: [2005, 2015],
				format: wNumb({
					decimals: 0,
				})
			});
			var firstValues = [
				document.getElementById('filter__years-start'),
				document.getElementById('filter__years-end')
			];
			firstSlider.noUiSlider.on('update', function( values, handle ) {
				firstValues[handle].innerHTML = values[handle];
			});
		} else {
			return false;
		}
		return false;
	}
	$(window).on('load', initializeFirstSlider());

	/*2*/
	function initializeSecondSlider() {
		if ($('#filter__imbd').length) {
			var secondSlider = document.getElementById('filter__imbd');
			noUiSlider.create(secondSlider, {
				range: {
					'min': 0,
					'max': 10
				},
				step: 0.1,
				connect: true,
				start: [2.5, 8.6],
				format: wNumb({
					decimals: 1,
				})
			});

			var secondValues = [
				document.getElementById('filter__imbd-start'),
				document.getElementById('filter__imbd-end')
			];

			secondSlider.noUiSlider.on('update', function( values, handle ) {
				secondValues[handle].innerHTML = values[handle];
			});

			$('.filter__item-menu--range').on('click.bs.dropdown', function (e) {
				e.stopPropagation();
				e.preventDefault();
			});
		} else {
			return false;
		}
		return false;
	}
	$(window).on('load', initializeSecondSlider());

	/*3*/
	function initializeThirdSlider() {
		if ($('#slider__rating').length) {
			var thirdSlider = document.getElementById('slider__rating');
			noUiSlider.create(thirdSlider, {
				range: {
					'min': 0,
					'max': 10
				},
				connect: [true, false],
				step: 0.1,
				start: 8.6,
				format: wNumb({
					decimals: 1,
				})
			});

			var thirdValue = document.getElementById('form__slider-value');

			thirdSlider.noUiSlider.on('update', function( values, handle ) {
				thirdValue.innerHTML = values[handle];
			});
		} else {
			return false;
		}
		return false;
	}
	$(window).on('load', initializeThirdSlider());

	/*==============================
	Clear Button
	==============================*/
	// Get the input field and clear button by their IDs
	const $searchInput = $('#searchInput');
	const $clearButton = $('#clearButton');

	// Add an input event listener to show/hide the clear button
	$searchInput.on('input', function() {
		if ($searchInput.val().trim() !== '') {
			// If there is text in the input field, show the clear button
			$clearButton.show();
		} else {
			// If the input is empty, hide the clear button
			$clearButton.hide();
		}
	});

	// Add a click event listener to the clear button
	$clearButton.on('click', function() {
		// Clear the input field's value
		$searchInput.val('');
		// Hide the clear button
		$clearButton.hide();  // Hide the clear button immediately after clearing the input
	});

	/*==============================
	Popup Buttons
	==============================*/
	// Get buttons by their IDs
	const openBtn = document.querySelectorAll(".card__add"); 
	const closeBtn = document.getElementById("closePopup");
	const xBtn = document.getElementById("closePopupAlt");
	const popup = document.getElementById("popup");
	console.log(popup);

	// Open the popup
	openBtn.forEach(x => x.addEventListener("click", () => {
		// console.log("clicked");		# Leave for testing purposes, modify as needed
		popup.classList.add("open");
	}))

	// Close the popup
	closeBtn.addEventListener("click", () => {
		popup.classList.remove("open");
	})
	// Close the popup with the x button
	xBtn.addEventListener("click", () => {
		popup.classList.remove("open");
	})
	// Redirect to login on click
	const loginBtn = document.getElementById("loginPopup");
	loginBtn.addEventListener("click", () => {
		window.location.href = "/login/";	// redirect to login page
    })


	/*==============================
	Popup add movie to watchlist
	==============================*/
	// STILL NOT WORKING, leaving this commented out for now
	// // Add movie to watchlist on click
	// const addToWatchlistBtn = document.getElementById('addToWatchlist');
	// const movieId = button.dataset.data-movie-id;
	// const watchlistId = button.dataset.data-watchlist-id; 

	// addToWatchlistBtn.addEventListener('click', () => {
	// // Add code here to handle adding movie to watchlist
	// });

	// // Add movie to watchlist
	// const addToWatchlist = (movieId, watchlistId) => {
	// 	fetch('/add-to-watchlist/', {
	// 	method: 'POST',
	// 	headers: {
	// 		'Content-Type': 'application/json',
	// 		'X-CSRFToken': csrftoken, 
	// 	},
	// 	body: JSON.stringify({
	// 		movie_id: movieId,
	// 		watchlist_id: watchlistId, 
	// 	})
	// 	})
	// 	.then(response => {
	// 	// Check for success
	// 	if (response.ok) {
	// 		// Movie added, update UI
	// 	} else {
	// 		// Handle error 
	// 	}
	// 	})
	// }


	/*==============================
    Popup add movie to watchlist
    ==============================*/
	const bookmarkLinks = document.querySelectorAll(".popup__add"); 
	bookmarkLinks.forEach(link => {
	  link.addEventListener('click', () => {
		console.log("TEST 1: clicked");
		const movieId = link.dataset.movieId;
		const watchlistId = link.dataset.watchlistId;
		add_movie_to_watchlist(movieId, watchlistId);
	  });
	});
	


	// Get DOM elements
	// const addToWatchlistBtn = document.getElementById('addToWatchlist');

	addToWatchlistBtn.addEventListener('click', handleAddToWatchlistClick);

	// Handle click event
	const handleAddToWatchlistClick = () => {

		// Get movieId and watchlistId from data attributes
		const movieId = addToWatchlistBtn.dataset.movieId; 
		const watchlistId = addToWatchlistBtn.dataset.watchlistId;

		// Call addToWatchlist function 
		addToWatchlist(movieId, watchlistId)
			.then(handleResponse) 
			.catch(handleError);

		// add_movie_to_watchlist(movieId, watchlistId) // Testing this as possible solution
	}

	// Make POST request to add movie to watchlist
	const addToWatchlist = async (movieId, watchlistId) => {

	// POST data
	const data = {
		movie_id: movieId,
		watchlist_id: watchlistId
	};

	// Request options
	const options = {
		method: 'POST',
		headers: {
		'Content-Type': 'application/json',
		'X-CSRFToken': csrftoken  
		},
		body: JSON.stringify(data)
	};

	// Make request and return response
	return fetch('/add-to-watchlist/', options)
		.then(res => res.json());

	}

	// Handle successful response 
	const handleResponse = (response) => {
	if (response.success) {
		// Movie added, update UI
	} else {
		// Show error 
	}
	}

	// Handle errors
	const handleError = (error) => {
	console.error(error);
	}

	// Event listener
	addToWatchlistBtn.addEventListener('click', handleAddToWatchlistClick);


});




// FULL COPY BELOW THIS LINE ********************************
// // Get DOM elements
// const addToWatchlistBtn = document.getElementById('addToWatchlist');

// // Handle click event
// const handleAddToWatchlistClick = () => {

//   // Get movieId and watchlistId from data attributes
//   const movieId = addToWatchlistBtn.dataset.movieId; 
//   const watchlistId = addToWatchlistBtn.dataset.watchlistId;

//   // Call addToWatchlist function 
//   addToWatchlist(movieId, watchlistId)
//     .then(handleResponse) 
//     .catch(handleError);

// }

// // Make POST request to add movie to watchlist
// const addToWatchlist = async (movieId, watchlistId) => {

//   // POST data
//   const data = {
//     movie_id: movieId,
//     watchlist_id: watchlistId
//   };
  
//   // Request options
//   const options = {
//     method: 'POST',
//     headers: {
//       'Content-Type': 'application/json',
//       'X-CSRFToken': csrftoken  
//     },
//     body: JSON.stringify(data)
//   };

//   // Make request and return response
//   return fetch('/add-to-watchlist/', options)
//     .then(res => res.json());

// }

// // Handle successful response 
// const handleResponse = (response) => {
//   if (response.success) {
//     // Movie added, update UI
//   } else {
//     // Show error 
//   }
// }

// // Handle errors
// const handleError = (error) => {
//   console.error(error);
// }

// // Event listener
// addToWatchlistBtn.addEventListener('click', handleAddToWatchlistClick);

