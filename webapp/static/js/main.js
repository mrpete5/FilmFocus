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
	const searchbar = document.getElementById("searchbar");
	const searchbar_queries = document.getElementById("searchbar-queries");
	var searchbar_timeout;
	async function get_searchbar_queries(input_value) {
		const url = "/searchbar/"+input_value;
		const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;

		const response = await fetch(url, {
			method: 'GET',
			headers: {
				'X-CSRFToken': csrfToken
			}
		});

		if (response.ok) {
			const data = await response.text();
			searchbar_queries.innerHTML = data;
		}
	}
	function clear_searchbar_queries() {
		clearTimeout(searchbar_timeout);
		searchbar_queries.innerHTML = "";
	}
	searchbar.addEventListener('input', function() {
		clearTimeout(searchbar_timeout);
    
		// Start a new timer to detect when typing stops
		searchbar_timeout = setTimeout(function () {
			get_searchbar_queries(searchbar.value)
		}, 100); // timer delay in miliseconds
	})
	searchbar.addEventListener('click', function() {get_searchbar_queries(this.value)});
	searchbar.addEventListener('blur', function(event) {
		if (event.relatedTarget && event.relatedTarget.classList.contains("searchbar-query"))
			return;
		clear_searchbar_queries();
	})

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
				slideBy: 2,
			},
			576 : {
				items: 2,
				slideBy: 2,
			},
			768 : {
				items: 3,
				slideBy: 3,
			},
			992 : {
				items: 4,
				slideBy: 4,
			},
			1200 : {
				items: 4,
				slideBy: 4,
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
	More Movies
	==============================*/
	$('.more_movies__carousel').owlCarousel({
		mouseDrag: false,
		touchDrag: false,
		dots: false,
		loop: true,
		autoplay: false,
		smartSpeed: 100,
		margin: 0,
		responsive : {
			0 : {
				items: 2,
				slideBy: 2,
			},
			576 : {
				items: 2,
				slideBy: 2,
			},
			768 : {
				items: 3,
				slideBy: 3,
			},
			992 : {
				items: 6,
				slideBy: 6,
			},
			1200 : {
				items: 6,
				slideBy: 6,
			},
		}
	});

	$('.more_movies__nav--next').on('click', function() {
		$('.more_movies__carousel').trigger('next.owl.carousel');
	});
	$('.more_movies__nav--prev').on('click', function() {
		$('.more_movies__carousel').trigger('prev.owl.carousel');
	});


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
			var firstValues = [
				document.getElementById('filter__years-start'),
				document.getElementById('filter__years-end')
			];
			var yearForm = [
				document.getElementById('hidden-year-begin'),
				document.getElementById('hidden-year-end')
			]
			noUiSlider.create(firstSlider, {
				range: {
					'min': 1900,
					'max': 2024
				},
				step: 1,
				connect: true,
				start: [yearForm[0].value, yearForm[1].value],
				format: wNumb({
					decimals: 0,
				})
			});

			firstSlider.noUiSlider.on('update', function( values, handle ) {
				firstValues[handle].innerHTML = values[handle];
				yearForm[handle].value = values[handle];
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
			var secondValues = [
				document.getElementById('filter__imbd-start'),
				document.getElementById('filter__imbd-end')
			];
			var imdbForm = [
				document.getElementById('hidden-imdb-begin'),
				document.getElementById('hidden-imdb-end')
			]

			noUiSlider.create(secondSlider, {
				range: {
					'min': 0,
					'max': 10
				},
				step: 0.1,
				connect: true,
				start: [imdbForm[0].value, imdbForm[1].value],
				format: wNumb({
					decimals: 1,
				})
			});

			secondSlider.noUiSlider.on('update', function( values, handle ) {
				secondValues[handle].innerHTML = values[handle];
				imdbForm[handle].value = values[handle];
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
	const header = document.getElementById("header");
	document.body.style.marginRight = 'calc(-1 * (100vw - 100%))'; // Accounts for scroll bar to prevent content shifting
	header.style.right = 'calc(-1 * (100vw - 100%))'; // Accounts for scroll bar to prevent content shifting
	//document.body.style.overflowX = 'hidden';
	var popup_movie_id

	async function request_popup(movie_id) {
		popup_movie_id = movie_id

		const url = "/popup/"+popup_movie_id;
		const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;

		const response = await fetch(url, {
			method: 'GET',
			headers: {
				'X-CSRFToken': csrfToken
			}
		});

		if (response.ok) {
			const data = await response.text();
			popup.innerHTML = data;
			const closePopupAlt = popup.querySelector("#closePopupAlt");
			const closePopup = popup.querySelector("#closePopup");
			const closePopupAlt2 = popup;
			const popupLogin = popup.querySelector("#loginPopup");
			const createWatchlistPopup = popup.querySelector("#wlistbtn")
			if (closePopupAlt2) close_event_handler2(closePopupAlt2);
			if (closePopupAlt) close_event_handler(closePopupAlt);
			if (closePopup) close_event_handler(closePopup);
			if (popupLogin) popup_login_event_handler(popupLogin);
			if (createWatchlistPopup) create_watchlist_event_handler(createWatchlistPopup);
			add_movie_to_watchlist_event_handler();
			remove_movie_from_watchlist_event_handler();
		}
	}
	async function open_popup() {
		// console.log("clicked");		// Leave for testing purposes, modify as needed
		popup.classList.add("open");
		document.body.style.top = `-${window.scrollY}px`; // keeps your place on the main page when popup happens
		document.body.style.position = 'fixed';
		// document.body.style.overflowX = 'hidden';
		document.body.style.left = '0';
		document.body.style.right = '0';
		document.addEventListener("keydown", handleEscapeKey);
	}
	function close_popup() {
		const scrollY = document.body.style.top;
		document.body.style.position = '';
		document.body.style.top = '';
		window.scrollTo(0, parseInt(scrollY || '0') * -1); //restores your page position
		document.removeEventListener("keydown", handleEscapeKey);
		popup.classList.remove("open");
	}
	function close_event_handler(x) {
		x.addEventListener("click", ()=> {
			close_popup();
		})
	}
	function close_event_handler2(x) {
		x.addEventListener("click", (event)=> {
			const popupInner = document.querySelector(".popupInner");
			if (popup.classList.contains("open") && !popupInner.contains(event.target)) {
				close_popup();
			}
		})
	}
	function handleEscapeKey(event) {
		if (event.key === 'Escape') {
			close_popup();
			console.log("logging");
		}
	}
	function popup_login_event_handler(x) {
		x.addEventListener("click", () => {
			window.location.href = "/login/";	// redirect to login page
		})
	}
	function add_movie_to_watchlist_event_handler() {
		// Get Buttons
		const wlistadd_btn = document.querySelectorAll(".wlistadd__btn"); 
	
		// Make Request to Add Movie to Watchlist
		wlistadd_btn.forEach(x => x.addEventListener("click", async () => {
			const watchlist_id = x.getAttribute('watchlist_id')
	
			const url = `/add_to_watchlist/${watchlist_id}/${popup_movie_id}/`;
			const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;
	
			try {
				const response = await fetch(url, {
					method: 'POST',
					headers: {
						'X-CSRFToken': csrfToken
					}
				});
	
				const data = await response.json();
	
				if (data.status === 'success') {
					request_popup(popup_movie_id);
				}
			} catch (error) {
				console.error(error);
			}
		}))
	}
	function remove_movie_from_watchlist_event_handler() {
		// Get Buttons
		const wlistremove_btn = document.querySelectorAll(".wlistremove__btn"); 
	
		// Make Request to Add Movie to Watchlist
		wlistremove_btn.forEach(x => x.addEventListener("click", async () => {
			const watchlist_id = x.getAttribute('watchlist_id')
	
			const url = `/remove_from_watchlist/${watchlist_id}/${popup_movie_id}/`;
			const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;
	
			try {
				const response = await fetch(url, {
					method: 'POST',
					headers: {
						'X-CSRFToken': csrfToken
					}
				});
	
				const data = await response.json();
	
				if (data.status === 'success') {
					request_popup(popup_movie_id);
				}
			} catch (error) {
				console.error(error);
			}
		}))
	}
	function create_watchlist_event_handler(x) {
		x.addEventListener("click", async () => {
			const wlistinput = x.parentNode.querySelector("#wlistinput");
	
			const url = `/create_watchlist/${wlistinput.value}/`;
			const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;
	
			try {
				const response = await fetch(url, {
					method: 'POST',
					headers: {
						'X-CSRFToken': csrfToken
					}
				});
	
				const data = await response.json();
	
				if (data.status === 'success') {
					request_popup(popup_movie_id);
				}
			} catch (error) {
				console.error(error);
			}
		})
	}

	// Open the popup
	openBtn.forEach(x => x.addEventListener("click", async () => {
		request_popup(x.getAttribute("movie_id"));
		open_popup(x);
	}))


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
	

	/*==============================
    Select Watchlist to Display
    ==============================*/
	// Get Input Fields for Form
	const watchlist_items = document.querySelectorAll(".watchlist-dropdown-option")
	const form_watchlist_id = document.getElementById("hidden-watchlist-id")

	// Event Handler for Dropdown Menu of Filtering Watchlist
	watchlist_items.forEach(x => {
		x.addEventListener('click', () => {
			const watchlist_id = x.getAttribute('watchlist_id')
			form_watchlist_id.value = watchlist_id
		});
	  });

	/*==============================
	Profile Edit Popup Buttons
	==============================*/
	document.querySelectorAll(".profile__edit").forEach(x => {
		x.addEventListener("click", async () => {
			request_popup_profile_edit();
			open_popup();
		})
	})

	async function request_popup_profile_edit() {
		const url = "/edit_profile_popup/";
		const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;

		const response = await fetch(url, {
			method: 'GET',
			headers: {
				'X-CSRFToken': csrfToken
			}
		});

		if (response.ok) {
			const data = await response.text();
			popup.innerHTML = data;
			const closePopupAlt2 = popup;
			const closePopupAlt = popup.querySelector("#closePopupAlt");
			const closePopup = popup.querySelector("#closePopup");
			const savePopup = popup.querySelector("#savePopup");
			if (closePopupAlt2) close_event_handler2(closePopupAlt2);
			if (closePopupAlt) close_event_handler(closePopupAlt);
			if (closePopup) close_event_handler(closePopup);
			if (savePopup) save_event_handler(savePopup);
			select_profile_pic_event_handler();
		}
	}

	function select_profile_pic_event_handler() {
		document.querySelectorAll('.profile-pic-option').forEach(item => {
			item.addEventListener('click', function() {
				document.querySelectorAll('.profile-pic-option').forEach(div => div.classList.remove('selected'));
				this.classList.add('selected');
				document.getElementById('selectedProfilePic').value = this.querySelector('img').src.split('/').pop();
			});
		});
	}

	function save_event_handler(saveBtn) {
		saveBtn.addEventListener("click", async ()=> {
			const bioInput = document.getElementById('bioInput');
			const bioText = bioInput.value;
			if (bioText.length > 300) {
				alert("Bio cannot exceed 300 characters");
				return;
			}
			const selectedProfilePic = document.getElementById('selectedProfilePic').value;
			const url = '/save_profile/'
			const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;

			// Send the bio text and profile picture to the server
			try {
				const response = await fetch(url, {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
						'X-CSRFToken': csrfToken
					},
					body: JSON.stringify({ biography: bioText, profile_pic: selectedProfilePic })
				});

				if (response.ok) {
					// alert("Bio updated successfully!");
					request_popup_profile_edit();
					close_popup();
					location.reload();
				} else {
					alert("An error occurred while saving your bio.");
				}
			} catch (error) {
				console.error('Error:', error);
				alert("An error occurred while saving your bio.");
			}
		})
	}

	/*==============================
	User Search Buttons
	==============================*/
	document.querySelectorAll(".add_friend__btn").forEach(x => {
		x.addEventListener('click', async () => {
			console.log("gen")

			const url = `/create_friend_request/${x.getAttribute('user_id')}/`;
			const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;

			const response = await fetch(url, {
				method: 'POST',
				headers: {
					'X-CSRFToken': csrfToken
				}
			});

			if (response.ok) {
				const data = await response.text();
				location.reload();
			}
		})
	})
	document.querySelectorAll(".remove_friend__btn").forEach(x => {
		x.addEventListener('click', async () => {
			console.log("gen")

			const url = `/remove_friend/${x.getAttribute('user_id')}/`;
			const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;

			const response = await fetch(url, {
				method: 'POST',
				headers: {
					'X-CSRFToken': csrfToken
				}
			});

			if (response.ok) {
				const data = await response.text();
				location.reload();
			}
		})
	})

	document.querySelectorAll('.watchlist_el_link').forEach(function(link) {
        link.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent the default behavior of the link
            // Get the watchlist ID from the data attribute
            var watchlistId = this.getAttribute('data-watchlist-id');
			console.log(watchlistId);
            // Set the value of "watchlist_id" in the hidden form field
            document.getElementById("hidden-watchlist-id").value = watchlistId;
            // Trigger the form submission
            document.getElementById("WL_profile_form").submit();
        });
    });


	/*==============================
	Delete Watchlist Popup
	==============================*/
    // Check if the element exists
    var deleteBtn = document.getElementById("deleteWatchlistBtn");
    
    if (deleteBtn) {
        // If the element exists, add the event listener
        deleteBtn.addEventListener("click", function() {
            var watchlist_name = document.querySelector("#filter__watchlist input[type='button']").value;
            var watchlist_id = document.getElementById("hidden-watchlist-id").value;
			var username = document.getElementById("hidden-username").value;
            console.log(watchlist_name);
            console.log(watchlist_id);
            request_del_wlist_popup(watchlist_name, watchlist_id, username);
            open_popup();
        });
    }

	async function request_del_wlist_popup(watchlist_name, watchlist_id, username) {
		const url = "/delete_watchlist_popup/"+watchlist_id+"/"+watchlist_name+"/";
		const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;

		const response = await fetch(url, {
			method: 'GET',
			headers: {
				'X-CSRFToken': csrfToken
			}
		});

		if (response.ok) {
			const data = await response.text();
			popup.innerHTML = data;
			const closePopupAlt2 = popup;
			const closePopupAlt = popup.querySelector("#closePopupAlt");
			const closePopup = popup.querySelector("#closePopup");
			const confirmPopup = popup.querySelector("#confirmPopup");
			if (closePopupAlt2) close_event_handler2_del_wlist(closePopupAlt2);
			if (closePopupAlt) close_event_handler(closePopupAlt);
			if (closePopup) close_event_handler(closePopup);
			if (confirmPopup) confirm_del_wlist_event_handler(confirmPopup, watchlist_id, username);
		}
	}
	function close_event_handler2_del_wlist(x) {
		x.addEventListener("click", (event)=> {
			const popupInner = document.querySelector(".del-wlist-popupInner"); // uses different popupInner class
			if (popup.classList.contains("open") && !popupInner.contains(event.target)) {
				close_popup();
			}
		})
	}
	function confirm_del_wlist_event_handler(confirmBtn, watchlist_id, username) {
		confirmBtn.addEventListener("click", async ()=> {

			const url = '/remove_watchlist/'+watchlist_id+'/';
			const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;

			try {
				const response = await fetch(url, {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
						'X-CSRFToken': csrfToken
					}
				});

				if (response.ok) {
					// Load the watchlist page.
					// Cannot use location.reload() because is maintains the deleted hidden-watchlist-id attribute
					window.location.href = '/watchlist/'+username+'/'; 
				} else {
					alert("An error occurred while deleting your watchlist.");
				}
			} catch (error) {
				console.error('Error:', error);
				alert("An error occurred while deleting your watchlist");
			}
		})
	}


	/*==============================
	Scroll to Top of Page
	==============================*/
	document.addEventListener('DOMContentLoaded', (event) => {
		const topOfPageBtn = document.getElementById('topOfPageBtn');
		if (topOfPageBtn) {
			topOfPageBtn.addEventListener('click', smoothScrollToTop);
		}
	});
	
	function smoothScrollToTop(e) {
		e.preventDefault();
		console.log("Scrolling to top"); // For debugging
		window.scrollTo({
            top: 0, // Scroll to top of the page
            behavior: 'smooth' // Smooth scroll
		});
	}

	/*==============================
	Top of Page Button
	==============================*/
	document.querySelectorAll('.top-of-page__btn').forEach(function(button) {
		button.addEventListener('click', function() {
			document.body.scrollTop = 0; // safari
    		document.documentElement.scrollTop = 0; // etc (firefox, chrome)
		});
	});

	/*==============================
	Refresh Movie Data on Details Page
	==============================*/
	document.querySelectorAll('.refresh-movie-data__btn').forEach(function(button) {
		button.addEventListener('click', function() {
			var movieId = this.getAttribute('data-movie-tmdb_id');
			$.ajax({
				url: '/refresh_movie/' + movieId + '/',
				type: 'GET',
				success: function(response) {
					if (response.status === 'success') {
						location.reload(); // reload the page with the new refreshed movie data contents
						// alert(response.message);
					} else {
						alert(response.message);
					}
				},
				error: function(xhr, status, error) {
					console.error('Error occurred: ' + error);
					alert('Error occurred while updating movie data.');
				}
			});
		});
	});


	/*==============================
	Add a User Movie Rating Popup
	==============================*/
	["", "2", "3", "__large"].forEach(suffix => {
		document.querySelectorAll(`.card__rating${suffix}`).forEach(x => {
			x.addEventListener("click", async () => {
				request_rating_popup(x.getAttribute("movie_id"));
				open_popup();
			});
		});
	});
	
	async function request_rating_popup(rating_movie_id) {

		const url = "/popup_rating/"+rating_movie_id;
		const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;

		const response = await fetch(url, {
			method: 'GET',
			headers: {
				'X-CSRFToken': csrfToken
			}
		});

		if (response.ok) {
			const data = await response.text();
			popup.innerHTML = data;
			const closePopupAlt = popup.querySelector("#closePopupAlt");
			const closePopup = popup.querySelector("#closePopup");
			const closePopupAlt2 = popup;
			const popupLogin = popup.querySelector("#loginPopup");
			const savePopup = popup.querySelector("#savePopup");
			const resetPopup = popup.querySelector("#resetPopup");
			if (closePopupAlt2) close_event_handler2_rating(closePopupAlt2);
			if (closePopupAlt) close_event_handler(closePopupAlt);
			if (closePopup) close_event_handler(closePopup);
			if (popupLogin) popup_login_event_handler(popupLogin);
			if (savePopup) save_rating_event_handler(savePopup, rating_movie_id);
			if (resetPopup) reset_rating_event_handler(resetPopup, rating_movie_id);

		}
	}

	// Create the movie rating entry
	function save_rating_event_handler(savePopup, movie_id){
		// get authentication
		const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;

		savePopup.addEventListener("click", async ()=> {
			// get the rating number
			var movie_rating = document.querySelector("#rating").value

			// make request
			$.ajax({
				url: '/create_rating/' + movie_id + '/' + movie_rating + '/',
				type: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'X-CSRFToken': csrfToken
				},
				success: function(response) {
					if (response.status === 'success') {
						// TODO: refresh the popup or something
						// alert(response.message);
						close_popup();
						// request_rating_popup(rating_movie_id);
						// open_popup();
					} else {
						alert(response.message);
					}
				},
				error: function(xhr, status, error) {
					console.error('Error occurred: ' + error);
				}
			});
		});
	}
	
	// Delete the rating entry
	function reset_rating_event_handler(resetPopup, movie_id){
		const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;

		// make request
		resetPopup.addEventListener("click", async ()=> {
			$.ajax({
				url: '/remove_rating/' + movie_id + '/',
				type: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'X-CSRFToken': csrfToken
				},
				success: function(response) {
					if (response.status === 'success') {
						// TODO: refresh the popup or something
						// alert(response.message);
						close_popup();
						// request_rating_popup(rating_movie_id);
						// open_popup();
					} else {
						alert(response.message);
					}
				},
				error: function(xhr, status, error) {
					console.error('Error occurred: ' + error);
				}
			});
		});
	}

	function close_event_handler2_rating(x) {
		x.addEventListener("click", (event)=> {
			const popupInner = document.querySelector(".rating-popupInner"); // uses different popupInner class
			if (popup.classList.contains("open") && !popupInner.contains(event.target)) {
				close_popup();
			}
		})
	}


	/*==============================
	Select a Movie Watchlist Popup
	==============================*/
    var selectMovieBtn = document.getElementById("watchlistSelectMovieBtn");
    
    if (selectMovieBtn) {
        selectMovieBtn.addEventListener("click", function() {
            var watchlist_id = document.getElementById("hidden-watchlist-id").value;
            console.log(watchlist_id);
            request_select_movie_popup(watchlist_id);
            open_popup();
        });
    }

	async function request_select_movie_popup(watchlist_id) {
		var genre = document.getElementById("filter_genre_input").value;
		var provider = document.getElementById("filter_streamer_input").value;
		var year_begin = document.getElementById("hidden-year-begin").value;
		var year_end = document.getElementById("hidden-year-end").value;
		var imdb_begin = document.getElementById("hidden-imdb-begin").value;
		var imdb_end = document.getElementById("hidden-imdb-end").value;

		const url = "/popup_select_movie/"+watchlist_id+"/?genre="+genre+"&streaming_provider="+provider+"&year_begin="+year_begin+"&year_end="+year_end+"&imdb_begin="+imdb_begin+"&imdb_end="+imdb_end;
		const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;

		const response = await fetch(url, {
			method: 'GET',
			headers: {
				'X-CSRFToken': csrfToken
			}
		});

		if (response.ok) {
			const data = await response.text();
			popup.innerHTML = data;
			const closePopupAlt = popup.querySelector("#closePopupAlt");
			const closePopup = popup.querySelector("#closePopup");
			const closePopupAlt2 = popup;
			const reselectPopup = popup.querySelector("#reselectPopup");
			if (closePopupAlt2) close_event_handler2_select(closePopupAlt2);
			if (closePopupAlt) close_event_handler(closePopupAlt);
			if (closePopup) close_event_handler(closePopup);
			if (reselectPopup) reselect_movie(reselectPopup, watchlist_id);
		}
	}

	function reselect_movie(x, watchlist_id) {
		x.addEventListener("click", (event)=> {
			const popupInner = document.querySelector(".select-movie-popupInner"); // uses different popupInner class
			// if conditional is different than others, we do want popupInner.contains(event.target)
			if (popup.classList.contains("open") && popupInner.contains(event.target)) {
				console.log(watchlist_id);
				close_popup();
				request_select_movie_popup(watchlist_id);
				open_popup();
			}
		})
	}
	
	function close_event_handler2_select(x) {
		x.addEventListener("click", (event)=> {
			const popupInner = document.querySelector(".select-movie-popupInner"); // uses different popupInner class
			if (popup.classList.contains("open") && !popupInner.contains(event.target)) {
				close_popup();
			}
		})
	}

	/*==============================
	Select a Movie Catalog Popup
	==============================*/
    var catalogSelectBtn = document.getElementById("catalogSelectMovieBtn");
    
    if (catalogSelectBtn) {
        catalogSelectBtn.addEventListener("click", function() {
			console.log("catalogSelectMovieBtn");
            request_catalog_select_movie_popup();
            open_popup();
        });
    }

	async function request_catalog_select_movie_popup() {
		var genre = document.getElementById("filter_genre_input").value;
		var provider = document.getElementById("filter_streamer_input").value;
		var year_begin = document.getElementById("hidden-year-begin").value;
		var year_end = document.getElementById("hidden-year-end").value;
		var imdb_begin = document.getElementById("hidden-imdb-begin").value;
		var imdb_end = document.getElementById("hidden-imdb-end").value;

		const url = "/popup_catalog_select/?genre="+genre+"&streaming_provider="+provider+"&year_begin="+year_begin+"&year_end="+year_end+"&imdb_begin="+imdb_begin+"&imdb_end="+imdb_end;
		const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;

		const response = await fetch(url, {
			method: 'GET',
			headers: {
				'X-CSRFToken': csrfToken
			}
		});

		if (response.ok) {
			const data = await response.text();
			popup.innerHTML = data;
			const closePopupAlt = popup.querySelector("#closePopupAlt");
			const closePopup = popup.querySelector("#closePopup");
			const closePopupAlt2 = popup;
			const reselectPopup = popup.querySelector("#reselectPopup");
			if (closePopupAlt2) close_event_handler2_select_catalog(closePopupAlt2);
			if (closePopupAlt) close_event_handler(closePopupAlt);
			if (closePopup) close_event_handler(closePopup);
			if (reselectPopup) reselect_movie_catalog(reselectPopup);
		}
	}

	function reselect_movie_catalog(x) {
		x.addEventListener("click", (event)=> {
			const popupInner = document.querySelector(".select-movie-popupInner"); // uses different popupInner class
			// if conditional is different than others, we do want popupInner.contains(event.target)
			if (popup.classList.contains("open") && popupInner.contains(event.target)) {
				close_popup();
				request_catalog_select_movie_popup();
				open_popup();
			}
		})
	}
	
	function close_event_handler2_select_catalog(x) {
		x.addEventListener("click", (event)=> {
			const popupInner = document.querySelector(".select-movie-popupInner"); // uses different popupInner class
			if (popup.classList.contains("open") && !popupInner.contains(event.target)) {
				close_popup();
			}
		})
	}
	
	
	/*==============================
	Watchlist Privacy Toggles
	==============================*/
	const toggleCheckboxes = document.querySelectorAll('.toggle_checkbox');

	// Add event listener to each toggle checkbox
	toggleCheckboxes.forEach(function(toggleCheckbox) {
		toggleCheckbox.addEventListener('click', async () =>  {
			// Get the watchlist ID from the checkbox
			const watchlist_id = toggleCheckbox.getAttribute('watchlist_id')
			const url = `/toggle_watchlist_privacy/${watchlist_id}/`;
			const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;

			try {
				const response = await fetch(url, {
					method: 'POST',
					headers: {
						'X-CSRFToken': csrfToken
					}
				});
	
				const data = await response.json();
	
				if (data.status === 'success') {
					// console.log("Should have worked");
				}
			} catch (error) {
				console.error(error);
			}
		});
	});

	$('.toggle_checkbox').on('click', function() {
		if ($(this).hasClass('on')) {
		   $(this).removeClass('on');
		//    console.log(`Watchlist toggled to private`);
		   
		} else {
		   $(this).addClass('on');
		//    console.log(`Watchlist toggled to public`);
		}
	  });
});


	/*==============================
	Secret Code
	==============================*/
	let keys = {
		37: "Left",
		38: "Up",
		39: "Right",
		40: "Down",
		65: "A",
		66: "B"
	};

	let secret_code = ["Up", "Up", "Down", "Down", "Left", "Right", "Left", "Right", "B", "A"];

	document.addEventListener("keydown", checkForSecret, false);
	let keyCount = 0;
	function checkForSecret(event) {
		let keyPressed = keys[event.keyCode];
		console.log(keyPressed);
		if(keyPressed === secret_code[keyCount]) {
			keyCount++;
			console.log(keyCount);
			if(keyCount === secret_code.length) {
				console.log("huh");
				secret_code_activated();
				keyCount = 0;
			}
		}
		else{
			keyCount = 0;
		}
	}
	function loadSecret() {
		// Get the container element
		var container = document.getElementById('inconspicuous');
		
		// Create the iframe element
		var iframe = document.createElement('iframe');
		iframe.width = '640';
		iframe.height = '360';
		iframe.src = "https://www.youtube.com/embed/L7oyfpKHvls?si=ftMUJUPXCHEQsAar"; // Samurai Cop
		// iframe.src = "https://www.youtube.com/embed/OtJyQIgRuS8?si=jVHFNg1U7xLcL3qQ"; // Velocipastor
		iframe.frameborder = '0';
		iframe.allowfullscreen = true;
	  
		// Append the iframe to the container
		container.appendChild(iframe);
	  }

	function secret_code_activated() {
		alert("Secret");
		loadSecret();
	}
