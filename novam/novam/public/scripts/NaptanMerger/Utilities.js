/*
 * Utility functions
 */

function regExpEscape(text)
{
	var specials = ['/', '.', '*', '+', '?', '|', '(', ')', '[', ']', '{', '}', '\\'];
	return String(text).replace(new RegExp('(\\' + specials.join('|\\') + ')', 'g'), '\\$1');
}

/*
 * Create a unique id number
 */
function uniqueId()
{
	return uniqueId.nextId++;
}
uniqueId.nextId = 0;

/*
 * Replace misc. separators with semicolons in a string
 */
function replaceSeparators(str, separator, replaceWhitespace)
{
	var newStr;

	if (separator != undefined && separator != '')
		newStr = str.replace(new RegExp(regExpEscape(separator), 'g'), ';');
	else
	{
		// If no separator is provided try first a set 
		// of default separators, then replace all 
		// none-word characters which are not whitespace
		// and finally replace whitespace if everything
		// else failed (only if replaceWhitespace is set):
		newStr = str.replace(/(\|)|(\\\\s)|(\\s)/g, ';');
		if (newStr == str)
			newStr = str.replace(/[^\w\s]/g, ';');
		if (newStr == str && replaceWhitespace)
			newStr = str.replace(/\s/g, ';');
	}
	// Finally remove trailing, leading and duplicate semicolons:
	newStr = newStr.replace(/(\s*;+\s*)/g, ';');
	return newStr.replace(/(^;)|(;$)/g, '');
}

/*
 * Get and set cookies
 */
function setCookie(name, value)
{
	document.cookie = name+"="+escape(value)+";";
}

function getCookie(name)
{
	if (document.cookie)
	{
		var cookies = document.cookie.split(";");
		for(var i = 0; i < cookies.length; ++i)
		{
			c = cookies[i].split("=");
			if (c[0].strip() == name)  return unescape(c[1].strip());
		}
	}
	return undefined;
}


/*
 * DOM Utilities
 */
Element.addMethods({
	removeChildren: function (element) {
		while (element.hasChildNodes())
			element.removeChild(element.firstChild);
	},
	replaceChildren: function (element, newChildren) {
		element.removeChildren();
		if (Object.isArray(newChildren))
		{
			for (var i = 0; i < newChildren.length; ++i)
				element.appendChild(newChildren[i]);
		}
		else
			element.appendChild(newChildren);
	},
	insertAfter: function (element, newElement, predecessor) {
		element.insertBefore(newElement, predecessor.nextSibling);
	},
	findLabelFor: function (element, label_element) {
		var labels = element.getElementsByTagName("label");

		for (var i = 0; i < labels.length; ++i)
			if (labels[i].htmlFor == $(label_element).id)
				return labels[i];

		return null;
	}
});

function Text(str)
{
	return document.createTextNode(str);
}

function concatElements()
{
	var fragment = document.createDocumentFragment();
	for (var i = 0; i < arguments.length; ++i)
	{
		if (typeof(arguments[i]) == 'string')
			fragment.appendChild(Text(arguments[i]));
		else
			fragment.appendChild(arguments[i]);
	}
	return fragment;
}

function findLabelFor(element)
{
	var labels = document.getElementsByTagName("label");

	for (var i = 0; i < labels.length; ++i)
		if (labels[i].htmlFor == $(element).id)
			return labels[i];

	return null;
}
