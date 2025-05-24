/*
*
*	Script.js - Scripts for My Python Trainer
*	Author: JC Web Technologies
*
*/



/* ***********
 * Not Required

$(document).ready(function () {
    $(".main_banner").slick({
        infinite: true,
        slidesToShow: 1,
        slidesToScroll: 1,
        autoplay: true,
        autoplaySpeed: 2000,
        dots: true,
    });
});

$(document).ready(function () {
    $(".slide_test").slick({
        infinite: true,
        slidesToShow: 3,
        slidesToScroll: 3,
        autoplay: true,
        autoplaySpeed: 2000,
        dots: true,
        responsive: [{
                breakpoint: 768,
                settings: {
                    arrows: false,
                    centerMode: true,
                    centerPadding: "20px",
                    slidesToShow: 2,
                },
            }, {
                breakpoint: 480,
                settings: {
                    arrows: false,
                    centerMode: true,
                    centerPadding: "40px",
                    slidesToShow: 1,
                },
            },
        ],
    });
});
 *****/

/* ============ JCWT Customized ============= */

$(document).ready(function () {

	// Student stories home page
	$(".slide_test").slick({
        infinite: true,
        slidesToShow: 3,
        slidesToScroll: 1, // Scroll one slide at a time for smoother transitions
        autoplay: true,
        autoplaySpeed: 3000, // Increase autoplay speed for better visibility
        dots: true,
        pauseOnHover: true, // Pause slider on hover
        responsive: [{
                breakpoint: 1024, // For tablets in landscape mode
                settings: {
                    slidesToShow: 2,
                    slidesToScroll: 1,
                    arrows: false,
                    dots: true,
                },
            }, {
                breakpoint: 768, // For tablets and smaller screens
                settings: {
                    slidesToShow: 2,
                    slidesToScroll: 2,
                    arrows: false,
                    centerMode: true,
                    centerPadding: "30px", // Increase padding for better focus on the current slide
                },
            }, {
                breakpoint: 576, // For smartphones in portrait mode
                settings: {
                    slidesToShow: 1,
                    slidesToScroll: 1,
                    arrows: false,
                    centerMode: true,
                    centerPadding: "20px",
                },
            }, {
                breakpoint: 480, // For small devices
                settings: {
                    slidesToShow: 1,
                    slidesToScroll: 1,
                    arrows: false,
                    centerMode: false, // Disable center mode for the smallest screens
                },
            },
        ],
    });

	// Close nav bar for mobile
    $("#closeNavbarMenu").on("click", function () {
        const navbarMenu = $("#navbarMenu")[0];
        const bsCollapse = new bootstrap.Collapse(navbarMenu, {
            toggle: true,
        });
        bsCollapse.hide();
    });

	// Course enrollment modal
    $('.enroll-course-modal').on('click', function () {
        $('#modalCourse').text($(this).data('course'));
        $('#modalBatchNumber').text($(this).data('batch'));
        $('#modalCoursePrice').text($(this).data('price'));
        $('#courseEnrollModalForm').attr('action', $(this).data('course-enroll-action'));
        $('#courseEnrollModal').modal('show');
    });

    /*
	new SimpleLightbox('.gallery a', {
		captions: true,
		captionType: 'attr',
		captionSelector: 'img',
		captionsData: 'alt',
		fadeSpeed: 250,
	});
     */

	// Certificate gallery
    $('.certificate-gallery a').each(function () {
        new SimpleLightbox(this, {
            captions: true,
            captionType: 'attr',
            captionSelector: 'img',
            captionsData: 'alt',
            fadeSpeed: 250,
            overlay: true,
            overlayOpacity: 0.5,
        });
    });

	// Awards and acheivements gallery
	new SimpleLightbox('.gallery a', {
		captions: true,
		captionType: 'attr',
		captionSelector: 'img',
		captionsData: 'alt',
		fadeSpeed: 250,
		overlay: true,
        overlayOpacity: 0.5,
	});

    // Password toggle
    const $togglePassword = $("#toggle-password");
    const $passwordInput = $('input[type="password"]');
    $togglePassword.on("click", function () {
        const type = $passwordInput.attr("type") === "password" ? "text" : "password";
        $passwordInput.attr("type", type);
        $(this).html(type === "password" ? "<i class='fa fa-eye fa-lg'></i>" : "<i class='fa fa-eye-slash fa-lg'></i>");
    });

	// Random quote loader for home page
    const quotes = [
        "A great Python trainer doesn't just teach code; they inspire curiosity and problem-solving.",
        "Python trainers build bridges between complexity and simplicity, making programming accessible to all.",
        "A Python trainer's real power lies in their ability to turn errors into learning opportunities.",
        "The best Python trainers are not just instructors but guides, leading students through the maze of code.",
        "A Python trainer's gift is transforming confusion into clarity with every line of code.",
        "True Python trainers ignite a passion for programming, turning novices into confident developers.",
        "In the hands of a great Python trainer, even the most difficult concepts become second nature.",
        "The most effective Python trainers teach not just syntax but the logic behind every algorithm.",
        "A good Python trainer empowers learners to not just write code but to think like a programmer.",
        "Python trainers shape the future by teaching not only a language, but the mindset to innovate."
    ];
	
    const randomQuote = quotes[Math.floor(Math.random() * quotes.length)];
    $("#random-quote").text(randomQuote);

});