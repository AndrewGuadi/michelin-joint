let batchCounter = 0;

$(document).ready(function() {
    $('.container').infiniteScroll({
        path: function() {
            let currentPath = window.location.pathname;
            if (currentPath.includes('/discover')) {
                return '/discover?page=' + (this.loadCount + 1);
            } else if (currentPath.includes('/search_results')) {
                let queryParams = new URLSearchParams(window.location.search);
                let query = queryParams.get('query') || '';
                let style = queryParams.get('style') || '';
                let star_count = queryParams.get('star_count') || '';
                return `/search_results?page=${this.loadCount + 1}&query=${query}&style=${style}&star_count=${star_count}`;
            }
        },
        append: '.container',
        history: false,
        status: '.page-load-status',
    });

    $('.container').on('append.infiniteScroll', function(event, response, path, items) {
        $(items).attr('data-batch', batchCounter);
        batchCounter++;

        // Optional: remove previous batches
        if (batchCounter > 1) {
            $('.container .custom-card[data-batch="' + (batchCounter - 2) + '"]').remove();
        }
    });

    $(window).on('scroll', function() {
        // Optionally, remove earlier batches when scrolling
        $('.container .custom-card[data-batch]').each(function() {
            if (isElementOutOfView($(this))) {
                $(this).remove();
            }
        });
    });
});

function isElementOutOfView(element) {
    const rect = element[0].getBoundingClientRect();
    return (rect.top < -window.innerHeight);  // Adjust as needed
}

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

// When the user clicks on the button, scroll to the top of the document
function topFunction() {
    document.body.scrollTop = 0; // For Safari
    document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
}
