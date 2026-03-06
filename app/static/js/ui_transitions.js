(() => {
	const ENTER_CLASS = "page-ready";
	const LEAVE_CLASS = "page-leaving";
	const LEAVE_DELAY_MS = 220;

	const isReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
	const hasBody = () => Boolean(document.body);

	function runEnterTransition() {
		if (!hasBody()) {
			return;
		}

		document.body.classList.remove(LEAVE_CLASS);
		if (isReducedMotion) {
			document.body.classList.add(ENTER_CLASS);
			return;
		}

		requestAnimationFrame(() => {
			document.body.classList.add(ENTER_CLASS);
		});
	}

	function shouldHandleLink(link, event) {
		if (!link || event.defaultPrevented) {
			return false;
		}

		if (event.button !== 0) {
			return false;
		}

		if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) {
			return false;
		}

		if (link.target && link.target !== "_self") {
			return false;
		}

		if (link.hasAttribute("download")) {
			return false;
		}

		const href = link.getAttribute("href");
		if (!href || href.startsWith("#") || href.startsWith("javascript:")) {
			return false;
		}

		const destination = new URL(link.href, window.location.href);
		if (destination.origin !== window.location.origin) {
			return false;
		}

		if (destination.href === window.location.href) {
			return false;
		}

		return true;
	}

	function navigateWithLeaveTransition(url) {
		if (!hasBody() || isReducedMotion) {
			window.location.href = url;
			return;
		}

		document.body.classList.remove(ENTER_CLASS);
		document.body.classList.add(LEAVE_CLASS);

		window.setTimeout(() => {
			window.location.href = url;
		}, LEAVE_DELAY_MS);
	}

	document.addEventListener("click", (event) => {
		const link = event.target.closest("a[href]");
		if (!shouldHandleLink(link, event)) {
			return;
		}

		event.preventDefault();
		navigateWithLeaveTransition(link.href);
	});

	window.addEventListener("pageshow", () => {
		runEnterTransition();
	});

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", runEnterTransition, { once: true });
	} else {
		runEnterTransition();
	}
})();
