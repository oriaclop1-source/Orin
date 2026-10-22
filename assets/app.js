/* primejersey.il — static storefront. Pages are rendered from data/catalog.json. */
(function () {
  'use strict';

  var cfg = window.SITE_CONFIG;
  var app = document.getElementById('App');
  var catalog = { products: [], collections: [] };
  var productsByHandle = {};
  var collectionsByHandle = {};

  var SIZE_ORDER = ['3XS', '2XS', 'XS', 'S', 'M', 'L', 'XL', '2XL', 'XXL', '3XL', '4XL', '5XL',
    '6', '8', '10', '12', '14', '16', '18', '20', '22', '24', '26', '28'];
  var SOUTH_AMERICA_CLUBS = ['פלמנגו', 'פלמגנו', 'flamengo', 'בוקה', 'boca', 'ריבר', 'river plate', 'פלומיננסה',
    'fluminense', 'פאלמיירס', 'palmeiras', 'סאו פאולו', 'sao paulo', 'são paulo', 'קורינתיאנס', 'corinthians',
    'גרמיו', 'gremio', 'grêmio', 'אינטרנסיונל', 'internacional', 'סנטוס', 'santos', 'ואסקו', 'vasco',
    'אתלטיקו מיניירו', 'atletico mineiro', 'atlético mineiro'];
  var RELATED_KEYS = [
    ['ריאל מדריד'], ['ברצלונה'], ['מנצ׳סטר יונייטד', 'מנצסטר יונייטד'], ['מנצ׳סטר סיטי', 'מנצסטר סיטי'],
    ['ליברפול'], ['ארסנל', 'ארנסל'], ['צ׳לסי', 'צלסי'], ['באיירן'], ['אינטר'], ['מילאן'], ['יובנטוס'],
    ['פ.ס.ז', 'פריז'], ['אתלטיקו'], ['ברזיל'], ['ארגנטינה'], ['איטליה'], ['אנגליה'], ['גרמניה'], ['הולנד'],
    ['ספרד'], ['צרפת'], ['פורטוגל'], ['יפן'], ['פלמנגו', 'פלמגנו'], ['בית״ר', 'בית"ר']
  ];

  // Header text of each collection page, taken from the store's custom collection sections.
  var COLLECTION_HEROES = {
    'רטרו': ['RETRO COLLECTION', 'קולקציית רטרו', 'חולצות רטרו קלאסיות של קבוצות ונבחרות מכל הזמנים — עיצובים אייקוניים, רגעים גדולים ונוסטלגיה אמיתית לאוהדי כדורגל.'],
    'חליפות-ילדים': ['KIDS FOOTBALL SETS', 'חליפות ילדים', 'חליפות כדורגל לילדים — נוחות, צבעוניות ומושלמות לאוהדים צעירים שאוהבים לשחק, להתאמן ולהרגיש כמו הכוכבים הגדולים.'],
    'מיסטרי-בוקס': ['MYSTERY BOX', 'מיסטרי בוקס', 'בוחרים סוג בוקס, מידה והעדפות — ואנחנו בוחרים עבורכם חולצה מפתיעה מתוך הקולקציה.'],
    'עונת-25-26': ['SEASON 25/26', 'קולקציית עונת 25/26', 'החולצות החדשות של עונת 2025/2026 — קבוצות, נבחרות, בית, חוץ ושלישית במקום אחד.'],
    'מונדיאל-2026': ['USA · CANADA · MEXICO — 2026', 'מונדיאל 2026', 'חולצות רשמיות של נבחרות העולם — היו מוכנים לגביע העולם 2026'],
    'נבחרות': ['NATIONAL TEAMS', 'קולקציית נבחרות', 'חולצות נבחרות לאומיות מכל העולם — קלאסיות, עונתיות ומהמונדיאל. לכל אוהד שמגאה בצבעי ארצו.'],
    'מוצרים-נוספים': ['EXTRA PRODUCTS', 'מוצרים נוספים', 'כל המוצרים המשלימים במקום אחד — אקססוריז, פריטים מיוחדים, שדרוגים, אביזרים וכל מה שמשלים את חוויית הכדורגל.'],
    'ליגיונרים': ['LEGIONNAIRES', 'ליגיונרים', 'החולצות של השחקנים הישראלים מעבר לים'],
    'stussy': ['STUSSY COLLECTION', 'STUSSY', 'קולקציית STUSSY — חולצות מיוחדות, עיצובים בולטים וסטייל רחוב שמתאים למי שרוצה משהו אחר.'],
    'שאר-העולם': ['REST OF THE WORLD', 'שאר העולם', 'חולצות מיוחדות מקבוצות ונבחרות מכל העולם — מחוץ לליגות המרכזיות, עם עיצובים שונים ומפתיעים.'],
    'nike-mind': ['NIKE MIND', 'NIKE MIND', 'קולקציית NIKE MIND — נעלי ספורט מיוחדות בצבעים בולטים, עם סטייל נקי ומחיר מבצע.'],
    'nba': ['NBA', 'NBA', 'קולקציית NBA — גופיות כדורסל, רטרו, קלאסיקות וספיישלים מהקבוצות הגדולות.'],
    'חליפות-אימון': ['TRAINING SUITS', 'חליפות אימון', 'חליפות אימון של קבוצות ונבחרות — נוחות, איכותיות ומתאימות ליום־יום.'],
    'premier-league': ['ENGLISH LEAGUE', 'הליגה האנגלית', 'חולצות מהכדורגל האנגלי — מנצ׳סטר יונייטד, ליברפול, ארסנל, צ׳לסי, סיטי ועוד קבוצות ענק במקום אחד.'],
    'spanish-league': ['SPANISH LEAGUE', 'הליגה הספרדית', 'חולצות מהכדורגל הספרדי — ריאל מדריד, ברצלונה, אתלטיקו מדריד ועוד קבוצות ענק מהלה ליגה במקום אחד.'],
    'italian-league': ['ITALIAN LEAGUE', 'הליגה האיטלקית', 'חולצות מהכדורגל האיטלקי — מילאן, אינטר, יובנטוס, נאפולי, רומא ועוד קבוצות ענק מהסרייה א׳ במקום אחד.'],
    'season-26-27': ['SEASON 26/27', 'עונת 2026/2027', 'החולצות החדשות של עונת 2026/2027 — בית, חוץ ושלישית של הקבוצות הגדולות.'],
    'special': ['SPECIAL COLLECTION', 'קולקציית ספיישלים', 'חולצות מיוחדות, עיצובים נדירים ודגמים שלא רואים בכל מקום.'],
    'israeli-league': ['ISRAELI LEAGUE', 'הליגה הישראלית', 'חולצות מהכדורגל הישראלי — מכבי חיפה, מכבי תל אביב, הפועל באר שבע, בית״ר ירושלים ועוד קבוצות מהליגה הישראלית במקום אחד.']
  };

  var HOME_CATEGORIES = [
    ['season-26-27', null, 'עונת 2026/2027'],
    ['מונדיאל-2026', 'home.png', 'מונדיאל 2026'],
    ['חליפות-ילדים', 'house.png', 'חליפות ילדים'],
    ['special', 'special.png', 'ספיישל'],
    ['רטרו', 'retro.png', 'רטרו'],
    ['ליגיונרים', 'noam.png', 'ליגיונרים'],
    ['מיסטרי-בוקס', 'mystery.png', 'מיסטרי בוקס'],
    ['premier-league', 'english.png', 'הליגה האנגלית'],
    ['spanish-league', 'spain.png', 'הליגה הספרדית'],
    ['italian-league', 'italy.png', 'הליגה האיטלקית'],
    ['israeli-league', 'israel.png', 'הליגה הישראלית'],
    ['stussy', 'stussy.png', 'STUSSY'],
    ['שאר-העולם', 'rest.png', 'שאר העולם']
  ];

  // Shopify's automatic "3+1 מתנה" discount: with 4+ items from these collections,
  // the cheapest one is free (once per order).
  var PROMO = {
    title: '3+1 מתנה',
    buy: 3,
    collections: ['רטרו', 'חליפות-ילדים', 'מיסטרי-בוקס', 'עונת-25-26', 'מונדיאל-2026', 'נבחרות',
      'מוצרים-נוספים', 'ליגיונרים', 'stussy', 'שאר-העולם', 'nike-mind', 'nba']
  };
  var promoHandles = {};

  var PAGE_SIZE = 96;

  /* ---------- helpers ---------- */

  function esc(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function money(amount) {
    return amount.toFixed(2) + ' ₪';
  }

  function shortMoney(amount) {
    return amount.toFixed(2).replace('.00', '') + ' ₪';
  }

  function themeAsset(name) {
    return cfg.themeAssetBase + name;
  }

  function img(url, width) {
    if (!url) {
      return '';
    }
    if (url.indexOf('cdn.shopify.com') === -1) {
      return url;
    }
    return url + (url.indexOf('?') === -1 ? '?' : '&') + 'width=' + width;
  }

  function productUrl(handle) {
    return '#/products/' + encodeURIComponent(handle);
  }

  function collectionUrl(handle) {
    return '#/collections/' + encodeURIComponent(handle);
  }

  function priceInfo(product) {
    var prices = product.var.map(function (v) { return v.p; });
    var min = Math.min.apply(null, prices);
    var max = Math.max.apply(null, prices);
    var compare = product.var.reduce(function (m, v) { return Math.max(m, v.c || 0); }, 0);
    return { min: min, varies: min !== max, compare: compare };
  }

  function priceLabel(product, fromWord) {
    var info = priceInfo(product);
    return info.varies ? fromWord + money(info.min) : money(info.min);
  }

  function lower(value) {
    return String(value || '').toLowerCase();
  }

  function optionKind(name) {
    var n = lower(name);
    if (name.indexOf('פאץ') !== -1 || name.indexOf('פאצ') !== -1 || n.indexOf('patch') !== -1) {
      return 'patch';
    }
    if (name.indexOf('שרוול') !== -1 || n.indexOf('sleeve') !== -1) {
      return 'sleeve';
    }
    if (name.indexOf('מיד') !== -1 || n.indexOf('size') !== -1) {
      return 'size';
    }
    return 'other';
  }

  function isNoPatch(value) {
    var v = lower(value);
    return value.indexOf('ללא') !== -1 || value.indexOf('בלי') !== -1 || v.indexOf('no patch') !== -1;
  }

  function isShortSleeve(value) {
    return value.indexOf('קצר') !== -1 || lower(value).indexOf('short') !== -1;
  }

  function isSouthAmericaClub(title) {
    var t = lower(title);
    return SOUTH_AMERICA_CLUBS.some(function (k) { return t.indexOf(lower(k)) !== -1; });
  }

  function storageGet(key, fallback) {
    try {
      var raw = window.localStorage.getItem(key);
      return raw ? JSON.parse(raw) : fallback;
    } catch (e) {
      return fallback;
    }
  }

  function storageSet(key, value) {
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (e) {
      /* private mode: cart lives only for this page view */
    }
  }

  /* ---------- cart ---------- */

  var cart = storageGet('pj_cart', []);

  function findVariant(product, options) {
    return product.var.find(function (v) {
      return v.o.every(function (value, i) { return value === options[i]; });
    });
  }

  function cartLines() {
    return cart.map(function (item) {
      var product = productsByHandle[item.h];
      var variant = product && findVariant(product, item.o);
      return product && variant ? { item: item, product: product, variant: variant } : null;
    }).filter(Boolean);
  }

  function cartTotals() {
    var lines = cartLines();
    var subtotal = 0;
    var count = 0;
    var promoUnitPrices = [];
    lines.forEach(function (line) {
      subtotal += line.variant.p * line.item.q;
      count += line.item.q;
      if (promoHandles[line.product.h]) {
        for (var i = 0; i < line.item.q; i++) {
          promoUnitPrices.push(line.variant.p);
        }
      }
    });
    var discount = 0;
    if (promoUnitPrices.length >= PROMO.buy + 1) {
      discount = Math.min.apply(null, promoUnitPrices);
    }
    return { lines: lines, subtotal: subtotal, discount: discount, total: subtotal - discount, count: count };
  }

  function saveCart() {
    storageSet('pj_cart', cart);
    renderCartDrawer();
    if (currentRoute().name === 'cart') {
      renderRoute();
    }
  }

  function addToCart(handle, options, name, number) {
    var key = [handle, options.join('|'), name, number].join('§');
    var existing = cart.find(function (item) { return item.k === key; });
    if (existing) {
      existing.q += 1;
    } else {
      cart.push({ k: key, h: handle, o: options, name: name, num: number, q: 1 });
    }
    saveCart();
    openCartDrawer();
  }

  function changeQty(key, delta) {
    cart = cart.map(function (item) {
      if (item.k === key) {
        item.q += delta;
      }
      return item;
    }).filter(function (item) { return item.q > 0; });
    saveCart();
  }

  function lineDetailsHtml(line) {
    var html = '';
    if (line.item.o.length) {
      html += '<div class="ballers-cart-drawer-variant">' + esc(line.item.o.join(' / ')) + '</div>';
    }
    if (line.item.name || line.item.num) {
      html += '<div class="ballers-cart-drawer-properties">';
      if (line.item.name) {
        html += '<div><strong>שם על החולצה:</strong> <span>' + esc(line.item.name) + '</span></div>';
      }
      if (line.item.num) {
        html += '<div><strong>מספר על החולצה:</strong> <span>' + esc(line.item.num) + '</span></div>';
      }
      html += '</div>';
    }
    return html;
  }

  function cartItemsHtml(lines) {
    return lines.map(function (line) {
      var image = line.product.img[0];
      return '<article class="ballers-cart-drawer-item">' +
        '<a href="' + productUrl(line.product.h) + '" class="ballers-cart-drawer-image">' +
          (image ? '<img src="' + esc(img(image, 260)) + '" alt="' + esc(line.product.t) + '" loading="lazy">' : '<span>אין תמונה</span>') +
        '</a>' +
        '<div class="ballers-cart-drawer-info">' +
          '<h3><a href="' + productUrl(line.product.h) + '">' + esc(line.product.t) + '</a></h3>' +
          lineDetailsHtml(line) +
          '<div class="ballers-cart-drawer-bottom">' +
            '<span class="qty-control">' +
              '<button type="button" data-qty="-1" data-key="' + esc(line.item.k) + '" aria-label="הפחתת כמות">−</button>' +
              '<span>כמות: ' + line.item.q + '</span>' +
              '<button type="button" data-qty="1" data-key="' + esc(line.item.k) + '" aria-label="הוספת כמות">+</button>' +
            '</span>' +
            '<strong>' + money(line.variant.p * line.item.q) + '</strong>' +
          '</div>' +
          '<div class="ballers-cart-drawer-actions">' +
            '<a href="' + productUrl(line.product.h) + '" class="ballers-cart-drawer-edit">ערוך בחירה</a>' +
            '<button type="button" class="ballers-cart-drawer-remove" data-qty="-' + line.item.q + '" data-key="' + esc(line.item.k) + '">הסר מוצר</button>' +
          '</div>' +
        '</div>' +
      '</article>';
    }).join('');
  }

  function totalsHtml(totals) {
    var html = '<div class="ballers-cart-drawer-total"><span>סכום ביניים</span><strong>' + money(totals.subtotal) + '</strong></div>';
    if (totals.discount > 0) {
      html += '<div class="ballers-cart-drawer-total promo-line"><span>' + esc(PROMO.title) + '</span><strong>−' + money(totals.discount) + '</strong></div>';
      html += '<div class="ballers-cart-drawer-total"><span>סה״כ לתשלום</span><strong>' + money(totals.total) + '</strong></div>';
    }
    return html;
  }

  function renderCartDrawer() {
    var drawer = document.getElementById('BallersCartDrawer');
    var totals = cartTotals();
    document.getElementById('CartCount').textContent = totals.count;

    var html = '<div class="ballers-cart-drawer-header"><div><h2>העגלה שלך</h2><p>' +
      (totals.count > 0 ? totals.count + ' פריטים בעגלה' : 'העגלה ריקה') +
      '</p></div><button type="button" class="ballers-cart-drawer-close" id="BallersCloseCartDrawer" aria-label="סגירת עגלה">×</button></div>';

    if (totals.count > 0) {
      html += '<div class="ballers-cart-drawer-items">' + cartItemsHtml(totals.lines) + '</div>' +
        '<div class="ballers-cart-drawer-footer">' + totalsHtml(totals) +
          '<p class="ballers-cart-drawer-note">משלוח חינם. את ההזמנה שולחים אלינו בוואטסאפ, והתשלום בביט.</p>' +
          '<a href="#/cart" class="ballers-cart-drawer-checkout">להשלמת ההזמנה</a>' +
          '<button type="button" class="ballers-cart-drawer-continue" id="BallersContinueShopping">המשך קנייה</button>' +
        '</div>';
    } else {
      html += '<div class="ballers-cart-drawer-empty"><h3>העגלה שלך ריקה</h3>' +
        '<p>אפשר להתחיל לבחור חולצות, חליפות ומוצרים מהחנות.</p>' +
        '<a href="#/" class="ballers-cart-drawer-empty-btn">חזרה לחנות</a></div>';
    }
    drawer.innerHTML = html;
  }

  function openCartDrawer() {
    document.getElementById('BallersCartDrawer').classList.add('open');
    document.getElementById('BallersCartDrawerOverlay').classList.add('open');
    document.body.style.overflow = 'hidden';
    var close = document.getElementById('BallersCloseCartDrawer');
    if (close) {
      close.focus();
    }
  }

  function closeCartDrawer() {
    document.getElementById('BallersCartDrawer').classList.remove('open');
    document.getElementById('BallersCartDrawerOverlay').classList.remove('open');
    document.body.style.overflow = '';
  }

  /* ---------- shared markup ---------- */

  function stripCardHtml(product) {
    var image = product.img[0];
    return '<article class="ballers-product-card">' +
      '<a href="' + productUrl(product.h) + '" class="ballers-image-box" tabindex="-1" aria-hidden="true">' +
        (image ? '<img src="' + esc(img(image, 800)) + '" alt="" loading="lazy">' : '<div class="ballers-image-placeholder">אין תמונה</div>') +
      '</a>' +
      '<div class="ballers-card-info">' +
        '<h3><a href="' + productUrl(product.h) + '">' + esc(product.t) + '</a></h3>' +
        '<p>' + priceLabel(product, 'החל מ- ') + '</p>' +
        '<a href="' + productUrl(product.h) + '" class="ballers-buy-btn" aria-label="לצפייה במוצר: ' + esc(product.t) + '">לצפייה במוצר</a>' +
      '</div>' +
    '</article>';
  }

  function gridCardHtml(product) {
    var info = priceInfo(product);
    var hasHover = product.img.length > 1;
    return '<article class="ballers-retro-card' + (hasHover ? ' has-hover-image' : '') + '">' +
      '<a href="' + productUrl(product.h) + '" class="ballers-retro-image-box" aria-label="' + esc(product.t) + '">' +
        (product.img[0]
          ? '<img src="' + esc(img(product.img[0], 900)) + '" alt="' + esc(product.t) + '" loading="lazy" class="ballers-retro-img-main">' +
            (hasHover ? '<img src="' + esc(img(product.img[1], 900)) + '" alt="' + esc(product.t) + '" loading="lazy" class="ballers-retro-img-hover">' : '')
          : '<div class="ballers-retro-no-image">אין תמונה</div>') +
      '</a>' +
      '<div class="ballers-retro-content">' +
        '<h2 class="ballers-retro-title"><a href="' + productUrl(product.h) + '">' + esc(product.t) + '</a></h2>' +
        '<div class="ballers-retro-price"><span>' + priceLabel(product, 'החל מ־') + '</span>' +
          (info.compare > info.min ? '<del>' + money(info.compare) + '</del>' : '') +
        '</div>' +
        '<a href="' + productUrl(product.h) + '" class="ballers-retro-button">לצפייה במוצר</a>' +
      '</div>' +
    '</article>';
  }

  function listingHtml(eyebrow, title, text, products, page, baseHash) {
    var pages = Math.max(1, Math.ceil(products.length / PAGE_SIZE));
    page = Math.min(Math.max(page, 1), pages);
    var shown = products.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

    var html = '<section class="ballers-retro-page" dir="rtl"><div class="ballers-retro-container">' +
      '<header class="ballers-retro-hero">' +
        (eyebrow ? '<div class="ballers-retro-eyebrow">' + esc(eyebrow) + '</div>' : '') +
        '<h1>' + esc(title) + '</h1>' +
        (text ? '<p>' + esc(text) + '</p>' : '') +
      '</header>';

    if (!products.length) {
      return html + '<div class="ballers-retro-empty"><h2>לא נמצאו מוצרים</h2><p>נסו חיפוש אחר או חזרו לעמוד הבית.</p></div></div></section>';
    }

    html += '<div class="ballers-retro-toolbar"><div class="ballers-retro-count">' + products.length + ' מוצרים</div>' +
      '<a class="ballers-retro-back-home" href="#/">חזרה לעמוד הבית</a></div>' +
      '<div class="ballers-retro-grid">' + shown.map(gridCardHtml).join('') + '</div>';

    if (pages > 1) {
      html += '<nav class="ballers-retro-pagination" aria-label="עמודי קולקציה">' +
        (page > 1 ? '<a href="' + baseHash + 'page=' + (page - 1) + '" class="ballers-retro-page-link">הקודם</a>' : '') +
        '<span class="ballers-retro-page-status">עמוד ' + page + ' מתוך ' + pages + '</span>' +
        (page < pages ? '<a href="' + baseHash + 'page=' + (page + 1) + '" class="ballers-retro-page-link">הבא</a>' : '') +
        '</nav>';
    }
    return html + '</div></section>';
  }

  /* ---------- pages ---------- */

  function renderHome() {
    var banner = cfg.seasonBanner;
    var html = '';
    if (banner && banner.image) {
      html += '<a href="' + esc(banner.link) + '" class="ballers-season-hero">' +
        '<img src="' + esc(img(banner.image, 2000)) + '" alt="' + esc(banner.alt) + '" loading="eager"></a>';
    }

    var best = cfg.bestSellers.map(function (h) { return productsByHandle[h]; }).filter(Boolean);

    html += '<section class="ballers-products-strip" dir="rtl" lang="he"><div class="ballers-container">' +
      '<div class="ballers-title-row"><span></span><h2>הנמכרים ביותר</h2><span></span></div>' +
      '<div class="ballers-strip-wrap">' +
        '<button class="ballers-arrow ballers-arrow-right" type="button" aria-label="ימינה"><span aria-hidden="true">‹</span></button>' +
        '<div class="ballers-products-row">' + best.map(stripCardHtml).join('') + '</div>' +
        '<button class="ballers-arrow ballers-arrow-left" type="button" aria-label="שמאלה"><span aria-hidden="true">›</span></button>' +
      '</div>';

    html += '<div class="ballers-title-row ballers-categories-title"><span></span><h2>קטגוריות</h2><span></span></div>' +
      '<div class="ballers-home-banners">' + HOME_CATEGORIES.map(function (c) {
        var isWorldCup = c[0] === 'מונדיאל-2026';
        var visual = c[1]
          ? '<span class="ballers-home-banner ballers-image-banner"><img src="' + esc(themeAsset(c[1])) + '" alt="" loading="lazy"></span>'
          : '<span class="ballers-home-banner ballers-image-banner season-badge" aria-hidden="true">26/27</span>';
        return '<a href="' + collectionUrl(c[0]) + '" class="ballers-home-banner-card' + (isWorldCup ? ' ballers-worldcup-card' : '') + '">' +
          visual + '<span class="ballers-home-banner-title' + (isWorldCup ? ' ballers-worldcup-title' : '') + '">' + esc(c[2]) + '</span></a>';
      }).join('') + '</div>';

    html += faqHtml() + '</div></section>';
    app.innerHTML = html;

    var row = app.querySelector('.ballers-products-row');
    function step() {
      var card = row.querySelector('.ballers-product-card');
      return card ? card.offsetWidth + 20 : 260;
    }
    app.querySelector('.ballers-arrow-left').addEventListener('click', function () {
      row.scrollBy({ left: -step(), behavior: 'smooth' });
    });
    app.querySelector('.ballers-arrow-right').addEventListener('click', function () {
      row.scrollBy({ left: step(), behavior: 'smooth' });
    });

    var gallery = app.querySelector('.ballers-customers-gallery');
    var pause = app.querySelector('.bcg-pause');
    pause.addEventListener('click', function () {
      var paused = gallery.classList.toggle('is-paused');
      pause.setAttribute('aria-pressed', paused ? 'true' : 'false');
      pause.textContent = paused ? 'המשך גלילה' : 'השהיית הגלילה';
    });
  }

  function faqHtml() {
    var faqs = [
      ['מה זמני המשלוח?', ['אנו שולחים הזמנות בין 7–15 ימי עסקים.', 'יכולים להיות עיכובים בעקבות מצב ביטחוני.']],
      ['מה מדיניות ההחזרות?', ['ניתן להחזיר מוצרים תוך 30 יום מיום הקנייה בתנאי שיש פגם או טעות במוצר.']],
      ['איך אני יכול לעקוב אחרי ההזמנה שלי?', ['כל שאלה בנושא המשלוח נא לפנות אלינו בטיקטוק או באינסטגרם.', 'אפשרי גם במספרי הטלפון שרשומים למטה.']],
      ['לאן החבילה שלי מגיעה?', ['החבילה מגיעה לנקודת חלוקה של EPOST הקרובה לביתכם.']]
    ];

    var photoCards = function (decorative) {
      return cfg.customerPhotos.map(function (file) {
        return '<article class="bcg-card"' + (decorative ? ' aria-hidden="true"' : '') + '>' +
          '<img src="' + esc(img(cfg.customerPhotoBase + file, 600)) + '" alt="' + (decorative ? '' : 'תמונה של לקוח עם חולצה שהזמין מהחנות') + '" loading="lazy">' +
          '<div class="bcg-stars"' + (decorative ? '' : ' role="img" aria-label="דירוג 5 מתוך 5"') + '><span aria-hidden="true">★★★★★</span><span class="bcg-stars-num" aria-hidden="true">5/5</span></div>' +
        '</article>';
      }).join('');
    };

    return '<section class="ballers-home-faq-contact" dir="rtl" aria-label="שאלות נפוצות ויצירת קשר">' +
      '<div class="ballers-faq-title"><h2 class="faq-title-gradient">שאלות נפוצות</h2><p>כל מה שחשוב לדעת לפני שמזמינים</p></div>' +
      '<div class="ballers-faq-list">' + faqs.map(function (f, i) {
        return '<details class="ballers-faq-item"' + (i === 0 ? ' open' : '') + '><summary><span>' + esc(f[0]) +
          '</span><span class="faq-arrow" aria-hidden="true">⌃</span></summary><div class="ballers-faq-answer">' +
          f[1].map(function (p) { return '<p>' + esc(p) + '</p>'; }).join('') + '</div></details>';
      }).join('') + '</div>' +
      '<section class="ballers-customers-gallery" dir="rtl" aria-labelledby="bcg-title">' +
        '<div class="bcg-header"><span class="bcg-kicker">לקוחות אמיתיים</span><h2 id="bcg-title">לקוחות מרוצים</h2>' +
        '<p>תמונות ופידבקים אמיתיים מהלקוחות שלנו</p><button class="bcg-pause" type="button" aria-pressed="false">השהיית הגלילה</button></div>' +
        '<div class="bcg-marquee-wrap" role="group" aria-label="תמונות של לקוחות עם החולצות שהזמינו"><div class="bcg-marquee-track">' +
          photoCards(false) + photoCards(true) +
        '</div></div>' +
        '<div class="bcg-footer"><span>רוצים להופיע כאן? שלחו לנו תמונה באינסטגרם או בטיקטוק</span></div>' +
      '</section>' +
      '<div class="ballers-contact-box"><div class="ballers-contact-title"><span>צריכים עזרה?</span><strong>דברו איתנו</strong></div>' +
        '<p>לשאלות, פניות והזמנות תתקשרו אלינו — אפשר להזמין גם בביט</p>' +
        '<div class="ballers-bit-badge"><strong>הזמנות ותשלום גם דרך Bit</strong></div>' +
        '<div class="ballers-contact-buttons">' + cfg.phones.map(function (phone) {
          return '<a href="tel:' + esc(phone.replace(/\D/g, '')) + '">' + esc(phone) + '</a>';
        }).join('') +
        '<a href="https://wa.me/' + esc(cfg.whatsappNumber) + '" target="_blank" rel="noopener">וואטסאפ</a></div>' +
      '</div>' +
    '</section>';
  }

  function renderCollection(handle, page) {
    var collection = collectionsByHandle[handle];
    if (!collection) {
      return renderNotFound();
    }
    var hero = COLLECTION_HEROES[handle] || ['', collection.t, ''];
    var products = collection.p.map(function (h) { return productsByHandle[h]; }).filter(Boolean);
    document.title = collection.t + ' – ' + cfg.shopName;
    app.innerHTML = listingHtml(hero[0], hero[1], hero[2], products, page, collectionUrl(handle) + '?');
  }

  function renderSearch(query, page) {
    var q = lower(query.trim());
    var terms = q.split(/\s+/).filter(Boolean);
    var results = terms.length ? catalog.products.filter(function (p) {
      var text = lower(p.t + ' ' + p.ty);
      return terms.every(function (t) { return text.indexOf(t) !== -1; });
    }) : [];
    document.title = 'חיפוש – ' + cfg.shopName;
    app.innerHTML = listingHtml('SEARCH', query ? 'תוצאות עבור: ' + query : 'חיפוש', '', results, page,
      '#/search?q=' + encodeURIComponent(query) + '&');
  }

  function renderProduct(handle) {
    var product = productsByHandle[handle];
    if (!product) {
      return renderNotFound();
    }
    document.title = product.t + ' – ' + cfg.shopName;

    var southAmerica = isSouthAmericaClub(product.t);
    var hasOptions = product.opt.length > 0;
    var first = product.var[0];

    var optionsHtml = product.opt.map(function (option, index) {
      var kind = optionKind(option.n);
      var values = option.v.slice();
      var labels = {};
      if (kind === 'size') {
        values.sort(function (a, b) {
          var ia = SIZE_ORDER.indexOf(a);
          var ib = SIZE_ORDER.indexOf(b);
          return (ia === -1 ? 999 : ia) - (ib === -1 ? 999 : ib);
        });
      }
      if (kind === 'patch' && southAmerica) {
        values = values.filter(function (v) {
          if (isNoPatch(v)) {
            labels[v] = 'ללא פאץ׳';
            return true;
          }
          if (v.indexOf('ליברטדור') !== -1 || lower(v).indexOf('libertadores') !== -1) {
            labels[v] = 'פאץ׳ ליברטדורס';
            return true;
          }
          return false;
        });
      }
      var label = kind === 'patch' ? (southAmerica ? 'בחר פאץ׳ ליברטדורס / ללא פאץ׳' : 'בחר פאץ׳ / ללא פאץ׳')
        : kind === 'size' ? 'בחר מידה'
        : kind === 'sleeve' ? 'בחר סוג שרוול'
        : 'בחר ' + option.n;
      return '<div class="ballers-option-group" data-option-kind="' + kind + '" data-index="' + index + '">' +
        '<label class="ballers-option-label">' + esc(label) + '</label>' +
        '<div class="ballers-option-values">' + values.map(function (v) {
          return '<button type="button" class="ballers-option-btn" data-index="' + index + '" data-value="' + esc(v) + '">' +
            '<span class="ballers-option-text">' + esc(labels[v] || v) + '</span><small class="ballers-option-extra-price"></small></button>';
        }).join('') + '</div></div>';
    }).join('');

    var gallery = '<button type="button" class="ballers-main-image-box" id="BallersOpenImageModal" aria-label="הגדלת תמונת מוצר">' +
      (product.img[0]
        ? '<img src="' + esc(img(product.img[0], 1200)) + '" data-full-image="' + esc(img(product.img[0], 1800)) + '" alt="' + esc(product.t) + '" class="ballers-main-product-image" loading="eager"><span class="ballers-zoom-hint">לחץ להגדלה</span>'
        : '<div class="ballers-no-image">אין תמונה</div>') +
      '</button>';
    if (product.img.length > 1) {
      gallery += '<div class="ballers-thumbs">' + product.img.slice(0, 8).map(function (src) {
        return '<button class="ballers-thumb-btn" type="button"><img src="' + esc(img(src, 180)) + '" data-main-src="' + esc(img(src, 1200)) +
          '" data-full-src="' + esc(img(src, 1800)) + '" alt="' + esc(product.t) + '" loading="lazy"></button>';
      }).join('') + '</div>';
    }

    var html = '<section class="ballers-product-page" dir="rtl"><div class="ballers-product-container"><div class="ballers-product-grid">' +
      '<div class="ballers-product-gallery">' + gallery + '</div>' +
      '<div class="ballers-product-info">' +
        '<div class="ballers-product-badge">מוצר נבחר</div>' +
        '<h1 class="ballers-product-title">' + esc(product.t) + '</h1>' +
        '<div class="ballers-product-price"><span id="BallersProductPrice">' + money(first.p) + '</span>' +
          (first.c ? '<del id="BallersComparePrice">' + money(first.c) + '</del>' : '<del id="BallersComparePrice" hidden></del>') + '</div>' +
        (product.d ? '<div class="ballers-product-description">' + product.d + '</div>' : '') +
        '<div class="ballers-size-box"><div class="ballers-size-head"><h3>טבלאות מידות</h3><p>מומלץ לבדוק מידה לפני הזמנה</p></div>' +
          '<div class="ballers-size-buttons"><button type="button" class="ballers-size-btn" data-size-modal="BallersSizeModalKids">טבלת מידות ילדים</button>' +
          '<button type="button" class="ballers-size-btn" data-size-modal="BallersSizeModalMature">טבלת מידות מבוגרים</button></div></div>' +
        '<form class="ballers-product-form" id="BallersProductForm" novalidate>' +
          (hasOptions ? '<div class="ballers-options">' + optionsHtml + '</div>' +
            '<div class="ballers-required-message" id="BallersRequiredMessage">יש לבחור מידה לפני הוספה לעגלה. ברירת המחדל היא ללא פאץ׳, ואפשר לשנות לפאץ׳ אחר.</div>' : '') +
          '<div class="ballers-print-note">רוצה חולצה חלקה? השאר את שדות השם והמספר ריקים.</div>' +
          '<div class="ballers-custom-fields">' +
            '<div class="ballers-field"><label for="BallersPlayerName">שם על החולצה</label><input id="BallersPlayerName" type="text" placeholder="לדוגמה: Messi" maxlength="20"></div>' +
            '<div class="ballers-field"><label for="BallersPlayerNumber">מספר על החולצה</label><input id="BallersPlayerNumber" type="text" placeholder="לדוגמה: 10" maxlength="3" inputmode="numeric"></div>' +
          '</div>' +
          '<div class="ballers-note-box">שם ומספר יועברו לבעל העסק יחד עם ההזמנה.</div>' +
          '<button type="submit" class="ballers-add-to-cart" id="BallersAddToCart">' + (hasOptions ? 'בחר מידה' : 'הוסף לעגלה') + '</button>' +
        '</form>' +
        '<div class="ballers-service-box"><h3>משלוחים ושירות</h3><p>אנו שולחים הזמנות בין 7–15 ימי עסקים.</p><p>ייתכנו עיכובים בעקבות המצב הביטחוני.</p></div>' +
      '</div></div>' + relatedHtml(product) + '</div>' +
      '<div class="ballers-image-modal" id="BallersImageModal"><button type="button" class="ballers-image-modal-close" aria-label="סגירה">×</button>' +
        '<div class="ballers-image-modal-inner"><img id="BallersModalImage" src="" alt="' + esc(product.t) + '"></div></div>' +
      '<div class="ballers-size-modal" id="BallersSizeModalKids"><div class="ballers-size-modal-content"><button type="button" class="ballers-size-close" aria-label="סגירה">×</button>' +
        '<h3>טבלת מידות ילדים</h3><img src="' + esc(themeAsset('kids.png')) + '" alt="טבלת מידות ילדים"></div></div>' +
      '<div class="ballers-size-modal" id="BallersSizeModalMature"><div class="ballers-size-modal-content"><button type="button" class="ballers-size-close" aria-label="סגירה">×</button>' +
        '<h3>טבלת מידות מבוגרים</h3><img src="' + esc(themeAsset('mature.png')) + '" alt="טבלת מידות מבוגרים"></div></div>' +
    '</section>';

    app.innerHTML = html;
    bindProductPage(product);
  }

  function relatedHtml(product) {
    var key = RELATED_KEYS.find(function (keys) {
      return keys.some(function (k) { return product.t.indexOf(k) !== -1; });
    });
    var pool = [];
    catalog.collections.forEach(function (c) {
      if (c.p.indexOf(product.h) !== -1 && !pool.length) {
        pool = c.p;
      }
    });
    var picked = [];
    var take = function (filter) {
      pool.forEach(function (h) {
        var p = productsByHandle[h];
        if (picked.length < 4 && p && p.h !== product.h && picked.indexOf(p) === -1 && filter(p)) {
          picked.push(p);
        }
      });
    };
    if (key) {
      take(function (p) { return key.some(function (k) { return p.t.indexOf(k) !== -1; }); });
    }
    take(function () { return true; });
    if (!picked.length) {
      return '';
    }
    return '<div class="ballers-related-section"><div class="ballers-related-title-wrap"><h2>מוצרים דומים</h2><p>עוד מוצרים שאולי יעניינו אותך</p></div>' +
      '<div class="ballers-related-grid">' + picked.map(function (p) {
        return '<article class="ballers-related-card"><a href="' + productUrl(p.h) + '" class="ballers-related-image">' +
          (p.img[0] ? '<img src="' + esc(img(p.img[0], 700)) + '" alt="' + esc(p.t) + '" loading="lazy">' : '<div class="ballers-related-no-image">אין תמונה</div>') +
          '</a><div class="ballers-related-info"><h3><a href="' + productUrl(p.h) + '">' + esc(p.t) + '</a></h3>' +
          '<div class="ballers-related-price">' + priceLabel(p, 'החל מ־') + '</div>' +
          '<a href="' + productUrl(p.h) + '" class="ballers-related-btn">לצפייה</a></div></article>';
      }).join('') + '</div></div>';
  }

  function bindProductPage(product) {
    var section = app.querySelector('.ballers-product-page');
    var groups = Array.prototype.slice.call(section.querySelectorAll('.ballers-option-group'));
    var buttons = Array.prototype.slice.call(section.querySelectorAll('.ballers-option-btn'));
    var addButton = document.getElementById('BallersAddToCart');
    var message = document.getElementById('BallersRequiredMessage');
    var priceEl = document.getElementById('BallersProductPrice');
    var compareEl = document.getElementById('BallersComparePrice');

    function selected() {
      return groups.map(function (g) {
        var active = g.querySelector('.ballers-option-btn.active');
        return active ? active.getAttribute('data-value') : null;
      });
    }

    function matches(variant, sel, skipIndex) {
      return variant.o.every(function (v, i) {
        return i === skipIndex || sel[i] === null || sel[i] === v;
      });
    }

    function minPriceFor(index, value) {
      var sel = selected();
      var pool = product.var.filter(function (v) { return v.o[index] === value && matches(v, sel, index); });
      if (!pool.length) {
        pool = product.var.filter(function (v) { return v.o[index] === value; });
      }
      return pool.length ? Math.min.apply(null, pool.map(function (v) { return v.p; })) : null;
    }

    function refresh() {
      var sel = selected();

      buttons.forEach(function (button) {
        var index = Number(button.getAttribute('data-index'));
        var value = button.getAttribute('data-value');
        var possible = product.var.some(function (v) { return v.o[index] === value && matches(v, sel, index) && !v.x; });
        button.classList.toggle('unavailable', !possible);

        var extra = button.querySelector('.ballers-option-extra-price');
        extra.textContent = '';
        extra.classList.remove('show');
        var group = button.closest('.ballers-option-group');
        var kind = group.getAttribute('data-option-kind');
        if (kind !== 'patch' && kind !== 'sleeve') {
          return;
        }
        if ((kind === 'patch' && isNoPatch(value)) || (kind === 'sleeve' && isShortSleeve(value))) {
          return;
        }
        var base = Array.prototype.slice.call(group.querySelectorAll('.ballers-option-btn')).map(function (b) {
          return b.getAttribute('data-value');
        }).find(function (v) { return kind === 'patch' ? isNoPatch(v) : isShortSleeve(v); });
        if (!base) {
          return;
        }
        var delta = (minPriceFor(index, value) || 0) - (minPriceFor(index, base) || 0);
        if (delta !== 0) {
          extra.textContent = (delta > 0 ? '+' : '-') + shortMoney(Math.abs(delta));
          extra.classList.add('show');
        }
      });

      var complete = sel.every(function (v) { return v !== null; });
      var variant = complete ? findVariant(product, sel) : null;
      var shownVariant = variant || product.var.find(function (v) { return matches(v, sel, -1); }) || product.var[0];
      priceEl.textContent = money(shownVariant.p);
      if (shownVariant.c) {
        compareEl.textContent = money(shownVariant.c);
        compareEl.hidden = false;
      } else {
        compareEl.hidden = true;
      }

      if (!complete) {
        addButton.textContent = 'בחר מידה';
        addButton.disabled = false;
      } else if (!variant) {
        addButton.textContent = 'השילוב שבחרת לא זמין';
        addButton.disabled = true;
      } else if (variant.x) {
        addButton.textContent = 'אזל מהמלאי';
        addButton.disabled = true;
      } else {
        addButton.textContent = 'הוסף לעגלה';
        addButton.disabled = false;
        if (message) {
          message.classList.remove('error');
        }
      }
    }

    groups.forEach(function (group) {
      if (group.getAttribute('data-option-kind') === 'patch') {
        var none = Array.prototype.slice.call(group.querySelectorAll('.ballers-option-btn')).find(function (b) {
          return isNoPatch(b.getAttribute('data-value'));
        });
        if (none) {
          none.classList.add('active');
        }
      }
    });

    buttons.forEach(function (button) {
      button.addEventListener('click', function () {
        var group = button.closest('.ballers-option-values');
        group.querySelectorAll('.ballers-option-btn').forEach(function (b) { b.classList.remove('active'); });
        button.classList.add('active');
        refresh();
      });
    });

    document.getElementById('BallersProductForm').addEventListener('submit', function (event) {
      event.preventDefault();
      var sel = selected();
      if (sel.some(function (v) { return v === null; })) {
        message.classList.add('error');
        message.textContent = 'לפני הוספה לעגלה חובה לבחור מידה.';
        message.scrollIntoView({ behavior: 'smooth', block: 'center' });
        return;
      }
      var variant = findVariant(product, sel);
      if (!variant || variant.x) {
        return;
      }
      addToCart(product.h, sel,
        document.getElementById('BallersPlayerName').value.trim(),
        document.getElementById('BallersPlayerNumber').value.trim());
    });

    var mainImage = section.querySelector('.ballers-main-product-image');
    section.querySelectorAll('.ballers-thumb-btn img').forEach(function (thumb) {
      thumb.parentElement.addEventListener('click', function () {
        mainImage.src = thumb.getAttribute('data-main-src');
        mainImage.setAttribute('data-full-image', thumb.getAttribute('data-full-src'));
      });
    });

    var imageModal = document.getElementById('BallersImageModal');
    document.getElementById('BallersOpenImageModal').addEventListener('click', function () {
      if (!mainImage) {
        return;
      }
      document.getElementById('BallersModalImage').src = mainImage.getAttribute('data-full-image');
      imageModal.classList.add('open');
    });
    imageModal.addEventListener('click', function (event) {
      if (event.target === imageModal || event.target.classList.contains('ballers-image-modal-close')) {
        imageModal.classList.remove('open');
      }
    });

    section.querySelectorAll('[data-size-modal]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        document.getElementById(btn.getAttribute('data-size-modal')).classList.add('open');
      });
    });
    section.querySelectorAll('.ballers-size-modal').forEach(function (modal) {
      modal.addEventListener('click', function (event) {
        if (event.target === modal || event.target.classList.contains('ballers-size-close')) {
          modal.classList.remove('open');
        }
      });
    });

    refresh();
  }

  function renderCart() {
    document.title = 'העגלה שלך – ' + cfg.shopName;
    var totals = cartTotals();
    var saved = storageGet('pj_customer', {});
    var html = '<section class="checkout-page" dir="rtl"><div class="checkout-container">' +
      '<header class="ballers-retro-hero"><div class="ballers-retro-eyebrow">YOUR CART</div><h1>העגלה שלך</h1></header>';

    if (!totals.count) {
      app.innerHTML = html + '<div class="ballers-cart-drawer-empty"><h3>העגלה שלך ריקה</h3><p>אפשר להתחיל לבחור חולצות, חליפות ומוצרים מהחנות.</p>' +
        '<a href="#/" class="ballers-cart-drawer-empty-btn">חזרה לחנות</a></div></div></section>';
      return;
    }

    var field = function (id, label, type, extra) {
      return '<div class="ballers-field"><label for="' + id + '">' + label + '</label><input id="' + id + '" name="' + id + '" type="' + type + '" value="' +
        esc(saved[id] || '') + '" ' + (extra || '') + '></div>';
    };

    html += '<div class="checkout-grid">' +
      '<div class="checkout-items ballers-cart-drawer-items">' + cartItemsHtml(totals.lines) + '</div>' +
      '<form class="checkout-form" id="CheckoutForm" novalidate>' +
        '<h2>פרטים למשלוח</h2>' +
        field('fullName', 'שם מלא', 'text', 'required autocomplete="name"') +
        field('phone', 'טלפון', 'tel', 'required autocomplete="tel" inputmode="tel"') +
        field('city', 'עיר', 'text', 'required autocomplete="address-level2"') +
        field('address', 'רחוב ומספר בית', 'text', 'required autocomplete="street-address"') +
        '<div class="ballers-field"><label for="notes">הערות להזמנה</label><textarea id="notes" name="notes" rows="3">' + esc(saved.notes || '') + '</textarea></div>' +
        '<fieldset class="checkout-pay"><legend>אמצעי תשלום</legend>' +
          ['Bit', 'PayBox', 'העברה בנקאית'].map(function (m, i) {
            return '<label><input type="radio" name="pay" value="' + m + '"' + ((saved.pay ? saved.pay === m : i === 0) ? ' checked' : '') + '> ' + m + '</label>';
          }).join('') +
        '</fieldset>' +
        '<div class="checkout-totals">' + totalsHtml(totals) + '<p class="ballers-cart-drawer-note">משלוח חינם לנקודת חלוקה של EPOST.</p></div>' +
        '<p class="checkout-error" id="CheckoutError" role="alert"></p>' +
        '<button type="submit" class="ballers-add-to-cart whatsapp-btn">שליחת ההזמנה בוואטסאפ</button>' +
        '<p class="checkout-hint">ייפתח וואטסאפ עם כל פרטי ההזמנה. שלחו את ההודעה, ונחזור אליכם עם פרטי התשלום.</p>' +
        '<button type="button" class="checkout-clear" id="ClearCart" hidden>ההזמנה נשלחה — ניקוי העגלה</button>' +
      '</form></div></div></section>';

    app.innerHTML = html;

    document.getElementById('CheckoutForm').addEventListener('submit', function (event) {
      event.preventDefault();
      var form = event.target;
      var data = {
        fullName: form.fullName.value.trim(),
        phone: form.phone.value.trim(),
        city: form.city.value.trim(),
        address: form.address.value.trim(),
        notes: form.notes.value.trim(),
        pay: form.pay.value
      };
      var error = document.getElementById('CheckoutError');
      if (!data.fullName || !data.phone || !data.city || !data.address) {
        error.textContent = 'נא למלא שם, טלפון, עיר וכתובת.';
        return;
      }
      if (data.phone.replace(/\D/g, '').length < 9) {
        error.textContent = 'מספר הטלפון לא נראה תקין.';
        return;
      }
      error.textContent = '';
      storageSet('pj_customer', data);
      window.open('https://wa.me/' + cfg.whatsappNumber + '?text=' + encodeURIComponent(orderMessage(data)), '_blank', 'noopener');
      document.getElementById('ClearCart').hidden = false;
    });

    document.getElementById('ClearCart').addEventListener('click', function () {
      cart = [];
      saveCart();
    });
  }

  function orderMessage(data) {
    var totals = cartTotals();
    var lines = ['הזמנה חדשה מהאתר ' + cfg.shopName, ''];
    totals.lines.forEach(function (line, i) {
      lines.push((i + 1) + '. ' + line.product.t);
      if (line.item.o.length) {
        lines.push('   ' + line.item.o.join(' / '));
      }
      if (line.item.name) {
        lines.push('   שם על החולצה: ' + line.item.name);
      }
      if (line.item.num) {
        lines.push('   מספר על החולצה: ' + line.item.num);
      }
      lines.push('   ' + line.item.q + ' × ' + money(line.variant.p) + ' = ' + money(line.variant.p * line.item.q));
    });
    lines.push('');
    lines.push('סכום ביניים: ' + money(totals.subtotal));
    if (totals.discount > 0) {
      lines.push(PROMO.title + ': −' + money(totals.discount));
    }
    lines.push('סה״כ לתשלום: ' + money(totals.total) + ' (משלוח חינם)');
    lines.push('');
    lines.push('שם: ' + data.fullName);
    lines.push('טלפון: ' + data.phone);
    lines.push('כתובת: ' + data.address + ', ' + data.city);
    lines.push('תשלום: ' + data.pay);
    if (data.notes) {
      lines.push('הערות: ' + data.notes);
    }
    return lines.join('\n');
  }

  function renderNotFound() {
    document.title = 'העמוד לא נמצא – ' + cfg.shopName;
    app.innerHTML = '<section class="ballers-retro-page" dir="rtl"><div class="ballers-retro-container"><div class="ballers-retro-empty">' +
      '<h2>העמוד לא נמצא</h2><p>ייתכן שהמוצר הוסר מהאתר.</p><a class="ballers-retro-back-home" href="#/">חזרה לעמוד הבית</a></div></div></section>';
  }

  /* ---------- routing ---------- */

  function currentRoute() {
    var hash = window.location.hash.replace(/^#/, '') || '/';
    var queryIndex = hash.indexOf('?');
    var path = queryIndex === -1 ? hash : hash.slice(0, queryIndex);
    var params = new URLSearchParams(queryIndex === -1 ? '' : hash.slice(queryIndex + 1));
    var parts = path.split('/').filter(Boolean).map(function (p) {
      try {
        return decodeURIComponent(p);
      } catch (e) {
        return p;
      }
    });
    var page = parseInt(params.get('page') || '1', 10) || 1;
    if (!parts.length) {
      return { name: 'home' };
    }
    if (parts[0] === 'collections' && parts[1]) {
      return { name: 'collection', handle: parts[1], page: page };
    }
    if (parts[0] === 'products' && parts[1]) {
      return { name: 'product', handle: parts[1] };
    }
    if (parts[0] === 'search') {
      return { name: 'search', q: params.get('q') || '', page: page };
    }
    if (parts[0] === 'cart') {
      return { name: 'cart' };
    }
    return { name: 'notfound' };
  }

  function renderRoute() {
    var route = currentRoute();
    closeCartDrawer();
    document.getElementById('BallersSearchPanel').classList.remove('open');

    if (route.name === 'home') {
      document.title = cfg.shopName;
      renderHome();
    } else if (route.name === 'collection') {
      renderCollection(route.handle, route.page);
    } else if (route.name === 'product') {
      renderProduct(route.handle);
    } else if (route.name === 'search') {
      renderSearch(route.q, route.page);
    } else if (route.name === 'cart') {
      renderCart();
    } else {
      renderNotFound();
    }

    var active = route.name === 'home' ? 'home' : route.handle;
    document.querySelectorAll('.ballers-nav-link').forEach(function (link) {
      var on = link.getAttribute('data-nav') === active;
      link.classList.toggle('active', on);
      if (on) {
        link.setAttribute('aria-current', 'page');
      } else {
        link.removeAttribute('aria-current');
      }
    });
  }

  /* ---------- header ---------- */

  function bindHeader() {
    document.querySelectorAll('[data-theme-asset]').forEach(function (el) {
      el.src = themeAsset(el.getAttribute('data-theme-asset'));
    });
    document.documentElement.style.setProperty('--asset-world', 'url("' + themeAsset('world.png') + '")');
    document.getElementById('Year').textContent = new Date().getFullYear();
    document.getElementById('Announcements').innerHTML = cfg.announcements.map(function (text) {
      return '<span>' + esc(text) + '</span>';
    }).join('');

    var toggle = document.querySelector('.ballers-search-toggle');
    var panel = document.getElementById('BallersSearchPanel');
    var input = panel.querySelector('.ballers-search-input');
    toggle.addEventListener('click', function () {
      var open = panel.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (open) {
        setTimeout(function () { input.focus(); }, 120);
      }
    });
    document.getElementById('SearchForm').addEventListener('submit', function (event) {
      event.preventDefault();
      window.location.hash = '#/search?q=' + encodeURIComponent(input.value.trim());
    });

    document.getElementById('BallersOpenCartDrawer').addEventListener('click', openCartDrawer);
    document.getElementById('BallersCartDrawerOverlay').addEventListener('click', closeCartDrawer);

    // Cart drawer and cart page buttons are re-rendered, so listen once on the document.
    document.addEventListener('click', function (event) {
      var target = event.target.closest('button, a');
      if (!target) {
        return;
      }
      if (target.id === 'BallersCloseCartDrawer' || target.id === 'BallersContinueShopping') {
        closeCartDrawer();
      } else if (target.hasAttribute('data-qty')) {
        changeQty(target.getAttribute('data-key'), Number(target.getAttribute('data-qty')));
      } else if (target.closest('.ballers-cart-drawer') && target.tagName === 'A') {
        closeCartDrawer();
      }
    });

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') {
        panel.classList.remove('open');
        closeCartDrawer();
        document.querySelectorAll('.ballers-image-modal.open, .ballers-size-modal.open').forEach(function (m) {
          m.classList.remove('open');
        });
      }
    });
  }

  /* ---------- start ---------- */

  bindHeader();
  renderCartDrawer();

  fetch('data/catalog.json')
    .then(function (res) { return res.json(); })
    .then(function (data) {
      catalog = data;
      catalog.products.forEach(function (p) { productsByHandle[p.h] = p; });
      catalog.collections.forEach(function (c) {
        collectionsByHandle[c.h] = c;
        if (PROMO.collections.indexOf(c.h) !== -1) {
          c.p.forEach(function (h) { promoHandles[h] = true; });
        }
      });
      cart = cart.filter(function (item) { return productsByHandle[item.h]; });
      renderCartDrawer();
      window.addEventListener('hashchange', function () {
        renderRoute();
        window.scrollTo(0, 0);
      });
      renderRoute();
    })
    .catch(function () {
      app.innerHTML = '<p class="load-error">לא הצלחנו לטעון את המוצרים. נסו לרענן את העמוד.</p>';
    });
})();
