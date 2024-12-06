const messages = {
	invalidemail: {
		text: "Please enter a complete email address in the form: yourname@yourdomain.com",
		type: "danger"
	},
	invalidzip: {
		text:
			'Please check your shipping zip code. It should be formatted like "12345" or "12345-0001"',
		type: "danger"
	},
	selectoptions: {
		text: "Please select all options before adding",
		type: "danger"
	},
	enterquantity: {
		text: "Please enter a quantity of at least 1",
		type: "danger"
	},
	addpers: {
		text: "Please personalize this item before adding",
		type: "danger"
	},
	addpersqty: {
		text: "Please enter personalization for the additional item(s)",
		type: "danger"
	},
	persrequired: {
		text: 'Before adding, please enter personalization for all fields, or the word "none"',
		type: "danger"
	},
	formincomplete: {
		text: "Please complete all fields",
		type: "danger"
	},
	badlogin: {
		text:
			"Please check your password and click the Forgot Password link if you need it replaced.",
		type: "danger"
	},
	fatal: {
		text: "There was a problem, please contact us.  We apologize for the inconvenience.",
		type: "danger"
	},
	loggedout: {
		text: "You are now logged out",
		type: "success"
	},
	loggedin: {
		text: "You are now logged in",
		type: "success"
	},
	emailsent: {
		text: "Sent! Please check your e-mail",
		type: "success"
	},
	itemremoved: {
		text: "Item removed",
		type: "success"
	},
	itemnotremoved: {
		text: "Problem removing an item from your cart, please contact us",
		type: "danger"
	},
	itemadded: {
		text: "Cart updated",
		type: "success"
	},
	itemnotadded: {
		text: "Problem adding item(s) to your cart.  Please contact us.",
		type: "danger"
	},
	itemupdated: {
		text: "Item updated",
		type: "success"
	},
	itemnotupdated: {
		text: "Problem updating item.  Please contact us.",
		type: "danger"
	},
	emptied: {
		text: "Emptied",
		type: "success"
	},
	cartcleared: {
		text: "Cart emptied",
		type: "success"
	},
	emailupdated: {
		text: "E-Mail updated",
		type: "success"
	},
	orderfail: {
		text: "Problem saving your order - please contact us",
		type: "danger"
	},
	contactfail: {
		text: "Problem submitting contact form - please call us",
		type: "danger"
	},
	contactsuccess: {
		text: "Sent!  We will be back to your shortly.",
		type: "success"
	},
	profileupdated: {
		text: "Profile updated",
		type: "success"
	},
	passwordupdated: {
		text: "Password updated",
		type: "success"
	},
	pwreset: {
		text: "Your password has been reset.  You are now logged in.",
		type: "success"
	},
	addressexists: {
		text: "This address already exists in your addressbook",
		type: "danger"
	},
	addressdeleted: {
		text: "Address removed",
		type: "success"
	},
	addressadded: {
		text: "Address added",
		type: "success"
	},
	addressupdated: {
		text: "Address updated",
		type: "success"
	},
	wishlistupdated: {
		text: "Wishlist updated",
		type: "success"
	},
	wishlistshared: {
		text: "Wishlist shared!",
		type: "success"
	},
	wishlistitemadded: {
		text: "Item added to wishlist",
		type: "success"
	},
	wishlistcleared: {
		text: "Wishlist cleared",
		type: "success"
	},
	wishlistitemnotadded: {
		text: "Problem adding to your wishlist - please contact us",
		type: "danger"
	},
	configureitem: {
		text: "Please select options before adding",
		type: "danger"
	},
	loginfirst: {
		text: "Please log in or sign up (hint: If you're new, registering takes only few seconds!)",
		type: "info"
	},
	subscribed: {
		text: "You are now subscribed.  Thank you!",
		type: "success"
	},
	clipboard: {
		text: "Copied to your clipboard",
		type: "success"
	}
};
export default messages;
