// Synchronous, bounded search helpers. No eval, subprocesses or network on input.

function finite(n) {
  if (typeof n !== "number" || !isFinite(n) || Math.abs(n) > 1e300) throw new Error("domain")
  return n === 0 ? 0 : n
}

function format(n) {
  n = finite(n)
  return Number(n.toPrecision(12)).toString()
}

function answer(kind, n, suffix, info) {
  var value = format(n)
  var label = value.replace(".", ",") + (suffix ? " " + suffix : "")
  return { kind: kind, label: label, copy: value + (suffix ? " " + suffix : ""),
    detail: "", info: info || "", number: n }
}

function factorial(n) {
  if (n < 0 || n > 170 || Math.floor(n) !== n) throw new Error("factorial")
  var result = 1
  for (var i = 2; i <= n; i++) result *= i
  return result
}

function trig(name, n) {
  var s = Math.sin(n), c = Math.cos(n)
  if (Math.abs(n) > 1e-12 && Math.abs(s) < 1e-14) s = 0
  if (Math.abs(c) < 1e-14) c = 0
  if (name === "sin") return s
  if (name === "cos") return c
  if (name === "tan") return s / c
  if (name === "cot") return c / s
  if (name === "sec") return 1 / c
  return 1 / s
}

function gcd(a, b) {
  a = Math.abs(a); b = Math.abs(b)
  if (!Number.isSafeInteger(a) || !Number.isSafeInteger(b)) throw new Error("integer")
  for (var i = 0; b && i < 128; i++) { var t = b; b = a % b; a = t }
  return a
}

var functionAliases = {
  "син": "sin", "синус": "sin", "кос": "cos", "косинус": "cos",
  "тг": "tan", "тангенс": "tan", "ctg": "cot", "ктг": "cot",
  "корень": "sqrt", "квкорень": "sqrt", "модуль": "abs",
  "lg": "log10", "arcsin": "asin", "arccos": "acos", "arctan": "atan",
  "tg": "tan", "факт": "fact", "среднее": "avg", "сумма": "sum"
}

function callFunction(name, args) {
  name = functionAliases[name] || name
  var a = args[0], b = args[1], result
  var unary = {
    sin: function(v) { return trig("sin", v) },
    cos: function(v) { return trig("cos", v) },
    tan: function(v) { return trig("tan", v) },
    asin: Math.asin, acos: Math.acos, atan: Math.atan,
    sinh: Math.sinh, cosh: Math.cosh, tanh: Math.tanh,
    asinh: Math.asinh, acosh: Math.acosh, atanh: Math.atanh,
    sqrt: Math.sqrt, cbrt: Math.cbrt, abs: Math.abs,
    ln: Math.log, log2: Math.log2, log10: Math.log10, exp: Math.exp,
    floor: Math.floor, ceil: Math.ceil, trunc: Math.trunc, sign: Math.sign,
    fact: factorial, factorial: factorial,
    deg: function(v) { return v * 180 / Math.PI },
    rad: function(v) { return v * Math.PI / 180 },
    sind: function(v) { return trig("sin", v * Math.PI / 180) },
    cosd: function(v) { return trig("cos", v * Math.PI / 180) },
    tand: function(v) { return trig("tan", v * Math.PI / 180) },
    cot: function(v) { return trig("cot", v) },
    sec: function(v) { return trig("sec", v) },
    csc: function(v) { return trig("csc", v) }
  }
  if (Object.prototype.hasOwnProperty.call(unary, name)) {
    if (args.length !== 1) throw new Error("arity")
    result = unary[name](a)
  } else if (name === "log") {
    if (args.length < 1 || args.length > 2) throw new Error("arity")
    result = Math.log(a) / Math.log(args.length === 2 ? b : 10)
  } else if (name === "round") {
    if (args.length < 1 || args.length > 2 || (args.length === 2 && (Math.abs(b) > 14 || Math.floor(b) !== b))) throw new Error("arity")
    var scale = Math.pow(10, args.length === 2 ? b : 0)
    result = Math.round(a * scale) / scale
  } else if (name === "pow" || name === "root" || name === "atan2" || name === "gcd" || name === "lcm" || name === "ncr" || name === "npr") {
    if (args.length !== 2) throw new Error("arity")
    if (name === "pow") result = Math.pow(a, b)
    else if (name === "root") result = a < 0 && b % 2 === 1 ? -Math.pow(-a, 1 / b) : Math.pow(a, 1 / b)
    else if (name === "atan2") result = Math.atan2(a, b)
    else if (name === "gcd") result = gcd(a, b)
    else if (name === "lcm") result = (a === 0 && b === 0) ? 0 : Math.abs(a / gcd(a, b) * b)
    else {
      if (!Number.isInteger(a) || !Number.isInteger(b) || b < 0 || a < b || a > 170) throw new Error("combinatorics")
      result = 1
      var count = name === "ncr" ? Math.min(b, a - b) : b
      for (var k = 1; k <= count; k++) result = result * (a - k + 1) / (name === "ncr" ? k : 1)
    }
  } else if (name === "min" || name === "max" || name === "sum" || name === "avg" || name === "hypot") {
    if (!args.length) throw new Error("arity")
    if (name === "min") result = Math.min.apply(Math, args)
    else if (name === "max") result = Math.max.apply(Math, args)
    else {
      result = 0
      for (var j = 0; j < args.length; j++) result += name === "hypot" ? args[j] * args[j] : args[j]
      if (name === "avg") result /= args.length
      if (name === "hypot") result = Math.sqrt(result)
    }
  } else throw new Error("unknown function")
  return finite(result)
}

function mathValue(input, previous) {
  var text = String(input).trim().toLowerCase()
  if (!text || text.length > 256) throw new Error("length")
  text = text.replace(/^[=\s]+/, "").replace(/[=\s]+$/, "")
    .replace(/×|·/g, "*").replace(/÷/g, "/").replace(/−|–/g, "-")
    .replace(/\*\*/g, "^").replace(/π/g, "pi").replace(/τ/g, "tau").replace(/φ/g, "phi")
    .replace(/√/g, "sqrt ").replace(/∛/g, "cbrt ")
    .replace(/(\d+(?:[.,]\d+)?)\s*(?:процент(?:а|ов|ы)?|percent)(?=\s|$)/g, "$1%")
    .replace(/\bmod\b/g, "%").replace(/\bof\b/g, "*").replace(/(^|\s)от(?=\s|$)/g, "$1*")
  // In multi-argument functions use a dot for decimals, or semicolon separators.
  if (text.indexOf(";") >= 0 || !/\b(pow|root|log|round|min|max|sum|avg|hypot|atan2|gcd|lcm|ncr|npr)\s*\(/.test(text))
    text = text.replace(/(\d),(?=\d)/g, "$1.")
  text = text.replace(/;/g, ",")
  var tokens = [], pos = 0
  while (pos < text.length) {
    var rest = text.slice(pos), match
    if (/^\s/.test(rest)) { pos++; continue }
    if ((match = /^(?:0x[0-9a-f]+|0b[01]+|0o[0-7]+|(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?)/.exec(rest))) {
      tokens.push({ type: "number", value: Number(match[0]) }); pos += match[0].length
    } else if ((match = /^[a-zа-яё_]+/.exec(rest))) {
      tokens.push({ type: "name", value: match[0] }); pos += match[0].length
    } else if (rest.slice(0, 2) === "//") {
      tokens.push({type: "//"}); pos += 2
    } else if (/^[+\-*/^%!(),°]/.test(rest)) {
      tokens.push({ type: rest.charAt(0), value: rest.charAt(0) }); pos++
    } else throw new Error("token")
    if (tokens.length > 200) throw new Error("length")
  }
  tokens.push({type: "end"})
  var index = 0, depth = 0
  var constants = { pi: Math.PI, e: Math.E, tau: 2 * Math.PI, phi: (1 + Math.sqrt(5)) / 2,
    ans: typeof previous === "number" ? previous : 0 }
  function value(n, percent) { return { n: finite(n), percent: !!percent } }
  function take(type) {
    if (tokens[index].type !== type) throw new Error("syntax")
    return tokens[index++]
  }
  function expr(minimum) {
    if (++depth > 32) throw new Error("depth")
    var token = tokens[index++], left
    if (token.type === "number") left = value(token.value)
    else if (token.type === "+" || token.type === "-") {
      var sign = expr(25); left = value(token.type === "-" ? -sign.n : sign.n, sign.percent)
    } else if (token.type === "(") { left = expr(0); take(")") }
    else if (token.type === "name") {
      if (Object.prototype.hasOwnProperty.call(constants, token.value)) left = value(constants[token.value])
      else {
        var args = []
        if (tokens[index].type === "(") {
          index++
          if (tokens[index].type !== ")") {
            args.push(expr(0).n)
            while (tokens[index].type === ",") { index++; args.push(expr(0).n) }
          }
          take(")")
        } else args.push(expr(25).n)
        left = value(callFunction(token.value, args))
      }
    } else throw new Error("syntax")

    while (true) {
      var next = tokens[index], op = next.type, binding = 0, implicit = false
      if (op === "!" || op === "°" || (op === "name" && /^(deg|град|градус|градусов|градуса)$/.test(next.value))) {
        if (40 < minimum) break
        index++
        left = value(op === "!" ? factorial(left.n) : left.n * Math.PI / 180)
        continue
      }
      if (op === "%" && tokens[index + 1].type !== "number" && tokens[index + 1].type !== "name" && tokens[index + 1].type !== "(") {
        if (40 < minimum) break
        index++; left = value(left.n / 100, true); continue
      }
      if (op === "+" || op === "-") binding = 10
      else if (op === "*" || op === "/" || op === "//" || op === "%") binding = 20
      else if (op === "^") binding = 30
      else if (op === "number" || op === "name" || op === "(") { binding = 20; implicit = true; op = "*" }
      else break
      if (binding < minimum) break
      if (!implicit) index++
      var right = expr(op === "^" ? binding : binding + 1), n
      if (op === "+") n = left.n + (right.percent ? left.n * right.n : right.n)
      else if (op === "-") n = left.n - (right.percent ? left.n * right.n : right.n)
      else if (op === "*") n = left.n * right.n
      else if (op === "/") n = left.n / right.n
      else if (op === "//") n = Math.floor(left.n / right.n)
      else if (op === "%") n = left.n % right.n
      else n = Math.pow(left.n, right.n)
      left = value(n)
    }
    depth--
    return left
  }
  var result = expr(0).n
  take("end")
  return finite(result)
}

var currencyAliases = {}
function addCurrency(code, aliases) {
  var names = (code.toLowerCase() + "|" + aliases).split("|")
  for (var i = 0; i < names.length; i++) currencyAliases[names[i]] = code
}
addCurrency("RUB", "rur|ruble|rubles|rouble|roubles|руб|рубль|рубля|рублей|рубли|рублях|рублю|рубле|р|₽")
addCurrency("USD", "dol|dollar|dollars|buck|bucks|дол|долл|доллар|доллара|долларов|доллары|долларах|доллару|долларе|бакс|бакса|баксов|баксы|доллар сша|доллары сша|$")
addCurrency("EUR", "euro|euros|ев|евр|евро|еврик|евриков|€")
addCurrency("CNY", "rmb|yuan|renminbi|юан|юань|юаня|юаней|юани|юанях|元")
addCurrency("KZT", "tenge|тен|тенге|тг|₸")
addCurrency("GBP", "pound|pounds|sterling|фун|фунт|фунта|фунтов|фунты|фунтах|£")
addCurrency("JPY", "yen|иен|йен|иена|иены|йена|йены|иенах|йенах|¥")
addCurrency("TRY", "lira|лир|лира|лиры|лиру|лирах|₺")
addCurrency("CHF", "franc|francs|франк|франка|франков|франки|швейцарский франк")
addCurrency("CAD", "канадский доллар|канадские доллары")
addCurrency("AUD", "австралийский доллар|австралийские доллары")
addCurrency("UAH", "грн|гривна|гривны|гривен|₴")
addCurrency("BYN", "бел руб|белорусский рубль|белорусские рубли")
addCurrency("GEL", "лари|лар|₾")
addCurrency("AMD", "драм|драма|драмов|֏")
addCurrency("AZN", "манат|маната|манатов|₼")
addCurrency("KGS", "сом|сома|сомов")
addCurrency("UZS", "сум|сума|сумов")
addCurrency("INR", "руп|рупия|рупии|рупий|₹")
addCurrency("AED", "дирхам|дирхама|дирхамов")
addCurrency("THB", "бат|бата|батов|฿")
addCurrency("KRW", "вон|вона|воны|₩")
addCurrency("PLN", "злот|злотый|злотых|злотые|zl|zł")
addCurrency("VND", "донг|донгов|₫")

function normalizeName(text) { return String(text).toLowerCase().replace(/\./g, "").replace(/\s+/g, " ").trim() }
function currencyCode(text, data) {
  var key = normalizeName(text)
  if (Object.prototype.hasOwnProperty.call(currencyAliases, key)) return currencyAliases[key]
  var code = key.toUpperCase()
  return /^[A-Z]{3}$/.test(code) && data && data.rates && data.rates[code] ? code : null
}

function splitConversion(text) {
  var parts = text.split(/\s*(?:->|→)\s*|\s+(?:в|во|to|in|into)\s+/i)
  return parts.length === 2 ? parts : [text]
}

function quantity(text, resolver) {
  var match = /^([+-]?(?:\d[\d _]*(?:[.,]\d+)?|[.,]\d+)(?:e[+-]?\d+)?)\s*(.*?)$/i.exec(text.trim())
  if (match && match[2]) {
    var unit = resolver(match[2])
    if (unit) return { amount: Number(match[1].replace(/[ _]/g, "").replace(",", ".")), unit: unit }
  }
  match = /^(.*?)\s*([+-]?(?:\d[\d _]*(?:[.,]\d+)?|[.,]\d+))$/i.exec(text.trim())
  if (match && match[1]) {
    var prefixUnit = resolver(match[1])
    if (prefixUnit) return {amount: Number(match[2].replace(/[ _]/g, "").replace(",", ".")), unit: prefixUnit}
  }
  return null
}

function currencyResult(query, data) {
  var text = query.trim(), isRate = /^(курс|курсы|rate|rates|exchange)\b/i.test(text)
  // JS word boundaries exclude Cyrillic letters.
  if (/^(курс|курсы)(?:\s|$)/i.test(text)) isRate = true
  text = text.replace(/^(?:курс|курсы|rate|rates|exchange)(?:\s+|$)/i, "").trim()
  var parts = splitConversion(text)
  var resolve = function(s) { return currencyCode(s, data) }
  var source = quantity(parts[0], resolve), target = parts.length === 2 ? resolve(parts[1]) : null
  if (!source) {
    var directCode = resolve(parts[0])
    if (directCode && (isRate || target)) source = {amount: 1, unit: directCode}
    else if (isRate && !text) source = {amount: 1, unit: "USD"}
  }
  if (!source || (parts.length === 2 && !target)) return null
  target = target || (source.unit === "RUB" ? "USD" : "RUB")
  if (!data || !data.rates || !data.rates[source.unit] || !data.rates[target])
    return {kind: "currency", label: "Курс недоступен", copy: "", detail: "", info: "Нет сохранённого курса"}
  var n = source.amount * data.rates[target] / data.rates[source.unit]
  var result = answer("currency", n, target)
  var compact = Math.abs(n) < 1 && n !== 0 ? Number(n.toPrecision(4)).toString() : n.toFixed(2)
  result.label = compact.replace(".", ",") + " " + target
  result.copy = compact + " " + target
  result.info = (data.provider || "") + " · " + (data.date || data.time_last_update_utc || "")
  if (data.fetched_at && Date.now() / 1000 - data.fetched_at > 2 * 86400)
    result.detail = "Сохранённый курс · " + (data.date || "")
  return result
}

var units = {}, exactUnits = {}
function addUnit(key, group, scale, symbol, aliases, offset) {
  var unit = {key: key, group: group, scale: scale, symbol: symbol, offset: offset || 0}
  units[key] = unit
  var names = (key + "|" + aliases).split("|")
  for (var i = 0; i < names.length; i++) units[normalizeName(names[i])] = unit
}
addUnit("m", "length", 1, "м", "м|метр|метра|метров|метры|meters|metres")
addUnit("km", "length", 1000, "км", "км|километр|километра|километров|kilometers")
addUnit("cm", "length", .01, "см", "см|сантиметр|сантиметра|сантиметров")
addUnit("mm", "length", .001, "мм", "мм|миллиметр|миллиметров")
addUnit("um", "length", 1e-6, "мкм", "μm|µm|мкм|микрометр")
addUnit("nm", "length", 1e-9, "нм", "нм|нанометр")
addUnit("mi", "length", 1609.344, "mi", "миля|мили|миль|mile|miles")
addUnit("ft", "length", .3048, "ft", "фут|фута|футов|foot|feet")
addUnit("in", "length", .0254, "in", "дюйм|дюйма|дюймов|inch|inches|\"")
addUnit("yd", "length", .9144, "yd", "ярд|ярда|ярдов|yard|yards")
addUnit("nmi", "length", 1852, "nmi", "морская миля|морских миль")
addUnit("kg", "mass", 1, "кг", "кг|килограмм|килограмма|килограммов")
addUnit("g", "mass", .001, "г", "г|гр|грамм|грамма|граммов|grams")
addUnit("mg", "mass", 1e-6, "мг", "мг|миллиграмм|миллиграммов")
addUnit("t", "mass", 1000, "т", "т|тонна|тонны|тонн|tonne")
addUnit("lb", "mass", .45359237, "lb", "lbs|фунт|фунта|фунтов|pound|pounds")
addUnit("oz", "mass", .028349523125, "oz", "унция|унции|унций|ounce|ounces")
addUnit("stone", "mass", 6.35029318, "st", "st|stones|стоун|стоуна")
addUnit("l", "volume", 1, "л", "л|литр|литра|литров|liter|litre|liters|litres")
addUnit("ml", "volume", .001, "мл", "мл|миллилитр|миллилитров")
addUnit("m3", "volume", 1000, "м³", "м3|м³|m³|кубометр|кубометров")
addUnit("gal", "volume", 3.785411784, "gal", "gallon|gallons|галлон|галлонов")
addUnit("qt", "volume", .946352946, "qt", "quart|quarts")
addUnit("pt", "volume", .473176473, "pt", "pint|pints|пинта|пинт")
addUnit("cup", "volume", .2365882365, "cup", "cups|чашка|чашки")
addUnit("m2", "area", 1, "м²", "м2|м²|m²|кв м")
addUnit("km2", "area", 1e6, "км²", "км2|км²|km²")
addUnit("cm2", "area", 1e-4, "см²", "см2|см²|cm²")
addUnit("ha", "area", 1e4, "га", "га|гектар|гектара|гектаров")
addUnit("acre", "area", 4046.8564224, "acre", "acres|акр|акров")
addUnit("ft2", "area", .09290304, "ft²", "ft²|sqft")
addUnit("m/s", "speed", 1, "м/с", "м/с|mps")
addUnit("km/h", "speed", 1 / 3.6, "км/ч", "км/ч|kph|kmh")
addUnit("mph", "speed", .44704, "mph", "миль/ч")
addUnit("knot", "speed", .514444444444, "kn", "kn|knots|узел|узлов")
addUnit("s", "time", 1, "с", "с|сек|секунда|секунды|секунд|sec|second|seconds")
addUnit("min", "time", 60, "мин", "мин|минута|минуты|минут|minute|minutes")
addUnit("h", "time", 3600, "ч", "ч|час|часа|часов|hour|hours|hr")
addUnit("d", "time", 86400, "дн", "дн|день|дня|дней|сутки|суток|day|days")
addUnit("week", "time", 604800, "нед", "w|нед|неделя|недели|недель|weeks")
addUnit("j", "energy", 1, "Дж", "дж|джоуль|джоулей|joule")
addUnit("kj", "energy", 1000, "кДж", "кдж|килоджоуль")
addUnit("cal", "energy", 4.184, "cal", "кал|калория|калорий")
addUnit("kcal", "energy", 4184, "ккал", "ккал|килокалория|килокалорий")
addUnit("wh", "energy", 3600, "Wh", "втч|вт⋅ч")
addUnit("kwh", "energy", 3600000, "kWh", "квтч|квт⋅ч")
addUnit("pa", "pressure", 1, "Pa", "па|паскаль|паскалей")
addUnit("kpa", "pressure", 1000, "kPa", "кпа")
addUnit("bar", "pressure", 100000, "bar", "бар|бара|баров")
addUnit("atm", "pressure", 101325, "atm", "атм|атмосфера|атмосфер")
addUnit("psi", "pressure", 6894.757293168, "psi", "psi")
addUnit("mmhg", "pressure", 133.322387415, "мм рт. ст.", "мм рт ст|ммртст")
addUnit("rad", "angle", 1, "rad", "рад|радиан|радиана|радианов")
addUnit("deg", "angle", Math.PI / 180, "°", "°|град|градус|градуса|градусов|degree|degrees")
addUnit("c", "temperature", 1, "°C", "°c|ц|°ц|цельсий|цельсия|celsius", 273.15)
addUnit("f", "temperature", 5 / 9, "°F", "°f|ф|фаренгейт|фаренгейта|fahrenheit", 255.3722222222222)
addUnit("k", "temperature", 1, "K", "°k|к|кельвин|кельвина|кельвинов|kelvin")

var dataPrefixes = ["", "k", "m", "g", "t", "p"]
for (var dp = 0; dp < dataPrefixes.length; dp++) {
  var prefix = dataPrefixes[dp], labelPrefix = prefix.toUpperCase()
  exactUnits[labelPrefix + "B"] = {group: "data", scale: Math.pow(1000, dp) * 8, symbol: labelPrefix + "B"}
  exactUnits[prefix + "B"] = exactUnits[labelPrefix + "B"]
  exactUnits[labelPrefix + "b"] = {group: "data", scale: Math.pow(1000, dp), symbol: labelPrefix + "b"}
  if (dp) {
    exactUnits[labelPrefix + "iB"] = {group: "data", scale: Math.pow(1024, dp) * 8, symbol: labelPrefix + "iB"}
    exactUnits[prefix + "iB"] = exactUnits[labelPrefix + "iB"]
  }
}
addUnit("byte", "data", 8, "B", "байт|байта|байтов|bytes|б")
addUnit("bit", "data", 1, "bit", "бит|бита|битов|bits")
addUnit("kb", "data", 8000, "KB", "кб|килобайт|килобайта|килобайтов")
addUnit("mb", "data", 8e6, "MB", "мб|мегабайт|мегабайта|мегабайтов")
addUnit("gb", "data", 8e9, "GB", "гб|гигабайт|гигабайта|гигабайтов")
addUnit("tb", "data", 8e12, "TB", "тб|терабайт|терабайта|терабайтов")
addUnit("kib", "data", 8 * 1024, "KiB", "киб|кибибайт")
addUnit("mib", "data", 8 * Math.pow(1024, 2), "MiB", "миб|мебибайт")
addUnit("gib", "data", 8 * Math.pow(1024, 3), "GiB", "гиб|гибибайт")
addUnit("tib", "data", 8 * Math.pow(1024, 4), "TiB", "тиб|тебибайт")

function unitCode(text) {
  var raw = String(text).trim()
  if (Object.prototype.hasOwnProperty.call(exactUnits, raw)) return exactUnits[raw]
  var key = normalizeName(raw)
  return Object.prototype.hasOwnProperty.call(units, key) ? units[key] : null
}

function unitResult(query) {
  var parts = splitConversion(query), source = quantity(parts[0], unitCode)
  if (!source) return null
  var target = parts.length === 2 ? unitCode(parts[1]) : null
  if (!target && parts.length === 1) {
    var defaults = {km: "mi", mi: "km", m: "cm", cm: "in", "in": "cm", mm: "cm", ft: "m", kg: "lb", lb: "kg", g: "kg", l: "ml", ml: "l", c: "f", f: "c", k: "c", h: "min", min: "s", d: "h"}
    target = unitCode(defaults[source.unit.key] || "")
  }
  if (!target || source.unit.group !== target.group) return null
  var baseline = source.amount * source.unit.scale + (source.unit.offset || 0)
  if (source.unit.group === "temperature" && baseline < -1e-10) return null
  return answer("conversion", (baseline - (target.offset || 0)) / target.scale, target.symbol)
}

var zoneAliases = {}
function addZone(id, label, aliases, fixed) {
  var data = {id: id, label: label, fixed: fixed}
  var keys = aliases.split("|")
  for (var i = 0; i < keys.length; i++) zoneAliases[keys[i]] = data
}
addZone("UTC", "UTC", "utc|gmt", 0)
addZone("Europe/Moscow", "Москва", "мск|москва|москве|мскв|moscow|msk", 180)
addZone("Asia/Novosibirsk", "Новосибирск", "нск|новосибирск|новосибирске|novosibirsk|nsk", 420)
addZone("Asia/Yekaterinburg", "Екатеринбург", "екб|екатеринбург|екатеринбурге|yekaterinburg", 300)
addZone("Asia/Krasnoyarsk", "Красноярск", "красноярск|красноярске|krasnoyarsk", 420)
addZone("Asia/Irkutsk", "Иркутск", "иркутск|иркутске|irkutsk", 480)
addZone("Asia/Vladivostok", "Владивосток", "владивосток|владивостоке|vladivostok", 600)
addZone("Europe/London", "Лондон", "лондон|лондоне|london")
addZone("Europe/Paris", "Париж", "париж|париже|paris")
addZone("Europe/Berlin", "Берлин", "берлин|берлине|berlin")
addZone("Europe/Istanbul", "Стамбул", "стамбул|стамбуле|istanbul", 180)
addZone("Asia/Dubai", "Дубай", "дубай|дубае|dubai", 240)
addZone("Asia/Tokyo", "Токио", "токио|япония|японии|tokyo|japan", 540)
addZone("Asia/Shanghai", "Пекин", "пекин|пекине|китай|китае|beijing|shanghai|china", 480)
addZone("Asia/Seoul", "Сеул", "сеул|сеуле|seoul", 540)
addZone("Asia/Bangkok", "Бангкок", "бангкок|бангкоке|bangkok", 420)
addZone("Asia/Almaty", "Алматы", "алматы|алмата|алмате|almaty", 300)
addZone("Asia/Kolkata", "Дели", "дели|индия|индии|delhi|india", 330)
addZone("America/New_York", "Нью-Йорк", "нью-йорк|нью йорк|нью-йорке|нью йорке|new york|nyc")
addZone("America/Los_Angeles", "Лос-Анджелес", "лос-анджелес|лос-анджелесе|los angeles|la")
addZone("America/Chicago", "Чикаго", "чикаго|chicago")
addZone("Australia/Sydney", "Сидней", "сидней|сиднее|sydney")
addZone("PST", "PST", "pst", -480)
addZone("PDT", "PDT", "pdt", -420)
addZone("EST", "EST", "est", -300)
addZone("EDT", "EDT", "edt", -240)

function zone(text) { return zoneAliases[normalizeName(text)] || null }
function offset(z, data) {
  if (typeof z.fixed === "number") return z.fixed
  if (data && data.offsets && typeof data.offsets[z.id] === "number") return data.offsets[z.id]
  throw new Error("timezone data")
}
function pad(n) { return String(n).length < 2 ? "0" + n : String(n) }
function timeResult(query, data, now) {
  var q = query.toLowerCase().trim(), match = /^(?:время|time|time in|local time)(?:\s+(?:в|in))?\s+(.+)$/.exec(q)
  var stamp = now === undefined ? Date.now() : now
  if (match) {
    var city = zone(match[1]); if (!city) return null
    var date = new Date(stamp + offset(city, data) * 60000)
    var text = pad(date.getUTCHours()) + ":" + pad(date.getUTCMinutes()) + " · " + city.label
    return {kind: "time", label: text, copy: text, detail: ""}
  }
  match = /^(\d{1,2}):(\d{2})\s+(.+?)\s+(?:в|to|in|→)\s+(.+)$/.exec(q)
  if (match) {
    var from = zone(match[3]), to = zone(match[4]), h = Number(match[1]), m = Number(match[2])
    if (!from || !to || h > 23 || m > 59) return null
    var minutes = h * 60 + m + offset(to, data) - offset(from, data)
    var shift = Math.floor(minutes / 1440)
    minutes = ((minutes % 1440) + 1440) % 1440
    var converted = pad(Math.floor(minutes / 60)) + ":" + pad(minutes % 60) + " · " + to.label
    if (shift) converted += shift > 0 ? " (+1 день)" : " (−1 день)"
    return {kind: "time", label: converted, copy: converted, detail: ""}
  }
  return null
}

function dateResult(query, now) {
  var q = query.toLowerCase().trim(), date = new Date(now === undefined ? Date.now() : now), match
  if (q === "дата" || q === "сегодня" || q === "today" || q === "date") { }
  else if (q === "завтра" || q === "tomorrow") date.setDate(date.getDate() + 1)
  else if (q === "вчера" || q === "yesterday") date.setDate(date.getDate() - 1)
  else if ((match = /^(?:через|in)\s+(\d+)\s+(день|дня|дней|days?|неделю|недели|недель|weeks?|месяц|месяца|месяцев|months?|год|года|лет|years?)$/.exec(q))) {
    var n = Number(match[1]); if (n > 100000) return null
    if (/^(месяц|month)/.test(match[2])) date.setMonth(date.getMonth() + n)
    else if (/^(год|лет|year)/.test(match[2])) date.setFullYear(date.getFullYear() + n)
    else date.setDate(date.getDate() + n * (/^(нед|week)/.test(match[2]) ? 7 : 1))
  } else if ((match = /^(\d{4}-\d{2}-\d{2})\s*-\s*(\d{4}-\d{2}-\d{2})$/.exec(q))) {
    var a = Date.parse(match[1]), b = Date.parse(match[2]); if (!isFinite(a) || !isFinite(b)) throw new Error("date")
    if (new Date(a).toISOString().slice(0, 10) !== match[1] || new Date(b).toISOString().slice(0, 10) !== match[2]) throw new Error("date")
    return answer("date", (a - b) / 86400000, "дн")
  } else return null
  var text = pad(date.getDate()) + "." + pad(date.getMonth() + 1) + "." + date.getFullYear()
  return {kind: "date", label: text, copy: text, detail: ""}
}

function baseResult(query) {
  var q = query.trim().toLowerCase(), match = /^(.*?)\s+(?:в|to|in|→)\s+(hex|bin|oct|dec|шестнадцатеричную|двоичную|восьмеричную|десятичную)$/.exec(q)
  if (!match) {
    var prefix = /^(hex|bin|oct|dec)\s+(.+)$/.exec(q)
    if (!prefix) return null
    match = [q, prefix[2], prefix[1]]
  }
  var source = match[1].trim(), n
  var marked = /^([0-9a-f]+)\s+(hex|bin|oct|dec)$/.exec(source)
  if (marked) {
    var radix = {hex: 16, bin: 2, oct: 8, dec: 10}[marked[2]]
    if (!(radix === 16 ? /^[0-9a-f]+$/ : radix === 2 ? /^[01]+$/ : radix === 8 ? /^[0-7]+$/ : /^\d+$/).test(marked[1])) return null
    n = parseInt(marked[1], radix)
  } else { try { n = mathValue(source) } catch (e) { return null } }
  if (!Number.isSafeInteger(n)) return null
  var target = match[2], result
  if (/^(hex|шест)/.test(target)) result = (n < 0 ? "-0x" : "0x") + Math.abs(n).toString(16).toUpperCase()
  else if (/^(bin|дво)/.test(target)) result = (n < 0 ? "-0b" : "0b") + Math.abs(n).toString(2)
  else if (/^(oct|вось)/.test(target)) result = (n < 0 ? "-0o" : "0o") + Math.abs(n).toString(8)
  else result = n.toString()
  return {kind: "base", label: result, copy: result, detail: "", number: n}
}

function evaluate(query, fxData, zoneData, previous, now) {
  var text = String(query || "").trim()
  if (!text || text.length > 256) return null
  try {
    var converted = currencyResult(text, fxData) || unitResult(text) || baseResult(text)
      || timeResult(text, zoneData, now) || dateResult(text, now)
    if (converted) return converted
    // Ordinary menu/application searches must not turn into calculator rows.
    if (!/\d|π|τ|φ|\bpi\b|\bans\b|\btau\b|\bphi\b/.test(text.toLowerCase()) && !/[a-zа-яё_]+\s*\(/i.test(text)) return null
    if (/^[+-]?\d+(?:[.,]\d+)?$/.test(text)) return null
    return answer("calculation", mathValue(text, previous))
  } catch (e) { return null }
}

if (typeof module !== "undefined") module.exports = {evaluate: evaluate, mathValue: mathValue, currencyResult: currencyResult, unitResult: unitResult, timeResult: timeResult}
