let batchCounter = 0;

// When the user clicks on the button, scroll to the top of the document
function topFunction() {
    document.body.scrollTop = 0; // For Safari
    document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
}

$(document).ready(function() {

        //For the top of page button
    //Get the button
    var mybutton = document.getElementById("scrollTopBtn");

    // When the user scrolls down 20px from the top of the document, show the button
    window.onscroll = function() {scrollFunction()};

    function scrollFunction() {
        if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
            mybutton.style.display = "block";
        } else {
            mybutton.style.display = "none";
        }
    }

    let isScrolling;
    let isLoading;
    if (isLoading) return null;
    $('.appended-data').infiniteScroll({
        path: function() {
            const totalPages = $('#total_pages').val(); // Value from a hidden input in the template
            const nextPage = this.loadCount + 2;
            console.log(totalPages, nextPage)
            if (nextPage > totalPages) {
                return null; // Stops the infinite scroll when all pages are loaded
            }

            let currentPath = window.location.pathname;
            if (currentPath.includes('/discover')) {
                return '/discover?page=' + nextPage;
            } else if (currentPath.includes('/search_results')) {
                let queryParams = new URLSearchParams(window.location.search);
                let query = queryParams.get('query') || '';
                let style = queryParams.get('style') || '';
                let star_count = queryParams.get('star_count') || '';
                return `/search_results?page=${nextPage}&query=${query}&style=${style}&star_count=${star_count}`;
            }
        },
        append: '.appended-data',
        history: false,
        status: '.page-load-status',
    });

    $('.appended-data').on('append.infiniteScroll', function(event, response, path, items) {
        isLoading = false;
        console.log('Append event triggered');
        console.log('Number of items being appended:', items.length);
        console.log('Batch counter:', batchCounter);
    
        $(items).attr('data-batch', batchCounter);
        batchCounter++;
    
        if (batchCounter > 1) {
            $('.appended-data .custom-card[data-batch="' + (batchCounter - 2) + '"]').remove();
        }
    })
    $('.appended-data').on('request.infiniteScroll', function(event, path) {
        isLoading = true;
    });

    $(window).on('scroll', function() {
        window.clearTimeout(isScrolling);
        isScrolling = setTimeout(function() {
            // Code to handle the scroll event
            $('.appended-data .custom-card[data-batch]').each(function() {
                if (isElementOutOfView($(this))) {
                    $(this).remove();
                }
            });

            // For the top of page button
            if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
                mybutton.style.display = "block";
            } else {
                mybutton.style.display = "none";
            }
        }, 66); // Adjust the timeout as needed (66ms is approximately 15 frames at 60Hz)
    })

    function isElementOutOfView(element) {
        const rect = element[0].getBoundingClientRect();
        return (rect.top < -window.innerHeight);  // Adjust as needed
    }


})