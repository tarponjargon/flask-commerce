import { safeString, formatPrice } from "../services/Utils";

const hbsHelpers = {
	eq: function (v1, v2) {
		return v1 === v2;
	},
	ne: function (v1, v2) {
		return v1 !== v2;
	},
	lt: function (v1, v2) {
		return v1 < v2;
	},
	gt: function (v1, v2) {
		return v1 > v2;
	},
	lte: function (v1, v2) {
		return v1 <= v2;
	},
	gte: function (v1, v2) {
		return v1 >= v2;
	},
	notexists: function (v1) {
		return !v1;
	},
	and: function () {
		return Array.prototype.slice.call(arguments).every(Boolean);
	},
	or: function () {
		return Array.prototype.slice.call(arguments, 0, -1).some(Boolean);
	},
	beginsWith: function (v1, v2) {
		return v1.startsWith(v2);
	},
	esc: function (str) {
		return safeString(str);
	},
	formatPrice: function (num) {
		return formatPrice(num);
	},
	filter: function (obj, key, value) {
		if (!Array.isArray(obj)) return false;
		return obj.filter((i) => i[key].toString() === value.toString())[0];
	},
	cfg: function (key) {
		return key in CFG ? CFG[key] : null;
	},
	math: function (lvalue, operator, rvalue) {
		lvalue = parseFloat(lvalue);
		rvalue = parseFloat(rvalue);
		return {
			"+": lvalue + rvalue,
			"-": lvalue - rvalue,
			"*": lvalue * rvalue,
			"/": lvalue / rvalue,
			"%": lvalue % rvalue,
		}[operator];
	},
};

export default hbsHelpers;
