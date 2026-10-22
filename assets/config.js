/*
  הגדרות האתר — זה הקובץ היחיד שצריך לערוך בשביל שינויים פשוטים.
  Site settings — the only file you normally need to edit.
*/
window.SITE_CONFIG = {
  shopName: 'primejersey.il',

  // WhatsApp number that receives orders (international format, no + or leading 0).
  // 0502174441 -> 972502174441
  whatsappNumber: '972502174441',

  // Phone numbers shown in the "דברו איתנו" box on the home page.
  phones: ['050-2174441', '052-8825211'],

  // Rotating texts in the blue bar at the top.
  announcements: ['משלוח חינם לכל הארץ', 'איכות מעולה', 'על כל האתר 3+1', 'שירות לקוחות זמין'],

  // Where theme images (logo, category pictures, size charts) are loaded from.
  // After running tools/download_images.py this becomes 'assets/img/theme/'.
  themeAssetBase: 'https://cdn.shopify.com/s/files/1/0843/2746/5200/t/8/assets/',

  // Big banner under the header on the home page.
  seasonBanner: {
    image: 'https://cdn.shopify.com/s/files/1/0843/2746/5200/files/46208.jpg',
    alt: 'עונת 2026/2027 יצאה לדרך, בואו להתחדש. שחקני כדורגל חוגגים באצטדיון.',
    link: '#/collections/season-26-27'
  },

  // "הנמכרים ביותר" row on the home page, in order (product handles).
  bestSellers: [
    'ריאל-מדריד-בית-26-27',
    'ברצלונה-חולצת-בית-26-27',
    'ברצלונה-חוץ-26-27',
    'mntzstr-syty-byt-26-27',
    'ריאל-מדריד-חוץ-2016-2017',
    'ברזיל-מודניאל-2002',
    'מנצסטר-יונייטד-2007-2008',
    'מנצסטר-יונייטד-בית-2007-2008',
    'ברזיל-מונדיאל-2010',
    'brtzlvnh-spyyshl',
    'lybrpvl-byt-2025-2026'
  ],

  // Customer photos in the "לקוחות מרוצים" strip.
  customerPhotos: [
    'WhatsApp_Image_2026-06-08_at_6.11.18_PM_1.jpg',
    'WhatsApp_Image_2026-06-08_at_4.00.41_PM_1.jpg',
    'WhatsApp_Image_2026-06-08_at_4.00.41_PM_4.jpg',
    'WhatsApp_Image_2026-06-08_at_4.00.41_PM_3.jpg',
    'WhatsApp_Image_2026-06-08_at_6.11.18_PM.jpg',
    'WhatsApp_Image_2026-06-08_at_4.03.27_PM.jpg',
    'WhatsApp_Image_2026-06-08_at_4.00.41_PM_2.jpg'
  ],
  customerPhotoBase: 'https://cdn.shopify.com/s/files/1/0843/2746/5200/files/'
};
