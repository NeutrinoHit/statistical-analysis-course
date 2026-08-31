(() => {
  "use strict";

  const lectures = [
    {number: "01", file: "00_introduction.html", enFile: "lecture-01-introduction.html", ru: "Мотивация и обзор курса", en: "Motivation and course overview", applets: [
      ["applet-gaussian-fit", "Псевдоданные и фит", "Gaussian pseudodata and fit"]
    ]},
    {number: "03", file: "02_characteristic_functions.html", ru: "Характеристические функции", en: "Characteristic functions", applets: [
      ["applet-fourier-clt", "Гауссов предел в пространстве Фурье", "Gaussian limit in Fourier space"]
    ]},
    {number: "04", file: "03_central_limit_theorem.html", ru: "Центральная предельная теорема", en: "Central limit theorem", applets: [
      ["applet-clt", "Центральная предельная теорема", "Central limit theorem"],
      ["applet-measurement-compatibility", "Совместимость двух измерений", "Compatibility of two measurements"]
    ]},
    {number: "05", file: "04_non_gaussian_clt_violations.html", ru: "Когда гауссов предел не возникает", en: "When the Gaussian limit fails", applets: [
      ["applet-cauchy-mean", "Среднее распределения Коши", "Mean of a Cauchy distribution"],
      ["applet-landau", "Распределение Ландау", "Landau distribution"],
      ["applet-correlated-error", "Коррелированная ошибка", "Correlated error"],
      ["applet-gaussian-mixture", "Смесь двух гауссовых распределений", "Mixture of two Gaussian distributions"],
      ["applet-gaussian-ratio", "Отношение гауссовых величин", "Ratio of Gaussian variables"]
    ]},
    {number: "06", file: "05_error_propagation.html", ru: "Распространение ошибок", en: "Error propagation", applets: [
      ["applet-nonlinear-propagation", "Граница линейного приближения", "Limits of linear error propagation"],
      ["applet-sample-standard-deviation", "Разброс оценки стандартного отклонения", "Sampling spread of the standard-deviation estimate"],
      ["applet-correlation-error", "Вклад корреляции в ошибку", "Correlation contribution to propagated uncertainty"]
    ]},
    {number: "07", file: "06_two_dimensional_gaussian.html", ru: "Двумерное гауссово распределение", en: "Two-dimensional Gaussian distribution", applets: [
      ["applet-correlation-ellipse", "Корреляция и эллипс", "Correlation and covariance ellipse"],
      ["applet-contour-probability", "Вероятность и размер контура", "Contour probability and size"]
    ]},
    {number: "08", file: "07_monte_carlo_method.html", ru: "Метод Монте-Карло", en: "Monte Carlo method", applets: [
      ["applet-rejection-sampling", "Метод отбора", "Rejection sampling"],
      ["applet-pi", "Оценка числа π", "Estimating π"],
      ["applet-grid-dimension", "Сетка в большой размерности", "A grid in high dimensions"],
      ["applet-rare-region", "Редкая область и равномерная генерация", "Rare region with uniform sampling"],
      ["applet-importance-sampling", "Выборка по важности", "Importance sampling"],
      ["applet-counting-ensemble", "Ансамбль счётных экспериментов", "Ensemble of counting experiments"]
    ]},
    {number: "09", file: "08_maximum_likelihood.html", ru: "Максимальное правдоподобие", en: "Maximum likelihood", applets: [
      ["applet-binomial-likelihood", "Биномиальное правдоподобие", "Binomial likelihood"]
    ]},
    {number: "10", file: "09_estimator_properties_profile_likelihood.html", ru: "Свойства оценок и профильное правдоподобие", en: "Estimator properties and profile likelihood", applets: [
      ["applet-variance-divisor", "Делитель N или N−1", "Divisor N or N−1"],
      ["applet-lifetime-likelihood", "Правдоподобие времени жизни", "Lifetime likelihood"],
      ["applet-profile-likelihood", "Профилирование мешающего параметра", "Profiling a nuisance parameter"],
      ["applet-oscillation-fit", "Осцилляционные параметры", "Oscillation parameters"]
    ]},
    {number: "11", file: "10_least_squares_linear_fit.html", ru: "Метод наименьших квадратов", en: "Least-squares method", applets: [
      ["applet-fit-geometry", "Геометрия ошибок линейной подгонки", "Uncertainty geometry of a linear fit"],
      ["applet-line-outlier", "Прямая, ошибки и выброс", "Line fit, uncertainties, and an outlier"]
    ]},
    {number: "13", file: "12_goodness_of_fit_and_significance.html", ru: "Качество согласия и значимость", en: "Goodness of fit and significance", applets: [
      ["applet-chi-square", "Распределение χ²", "Chi-square distribution"],
      ["applet-p-value", "p-уровень на графике", "The p-value on a distribution"],
      ["applet-test-statistic", "Распределение тестовой статистики", "Distribution of a test statistic"]
    ]}
  ];

  const root = document.querySelector("[data-lecture-applets]");
  if (!root) return;

  const locale = root.dataset.locale === "en" ? "en" : "ru";
  const slideBase = root.dataset.slideBase || "./";
  const localSlideBase = root.dataset.localSlideBase || "./";
  const words = locale === "ru"
    ? {lecture: "Лекция", open: "Открыть слайд отдельно", frame: "Интерактивный слайд"}
    : {lecture: "Lecture", open: "Open slide in a new tab", frame: "Interactive slide"};

  const makeUrl = (lecture, applet) => locale === "en" && lecture.enFile
    ? `${localSlideBase}${lecture.enFile}#/${applet[0]}`
    : `${slideBase}${lecture.file}#/${applet[0]}`;

  for (const lecture of lectures) {
    const group = document.createElement("section");
    group.className = "lecture-applet-group";
    const heading = document.createElement("h3");
    heading.innerHTML = `<span>${words.lecture} ${lecture.number}.</span> ${lecture[locale]}`;
    group.append(heading);

    const items = document.createElement("div");
    items.className = "lecture-applet-items";
    for (const applet of lecture.applets) {
      const url = makeUrl(lecture, applet);
      const details = document.createElement("details");
      details.className = "lecture-applet-row";
      details.innerHTML = `
        <summary>${applet[locale === "ru" ? 1 : 2]}</summary>
        <div class="lecture-applet-body">
          <iframe class="lecture-applet-frame" title="${words.frame}: ${applet[locale === "ru" ? 1 : 2]}" data-src="${url}" loading="lazy" allowfullscreen></iframe>
          <div class="lecture-applet-actions"><a class="link" href="${url}" target="_blank" rel="noopener">${words.open}</a></div>
        </div>`;
      details.addEventListener("toggle", () => {
        if (!details.open) return;
        const frame = details.querySelector("iframe[data-src]");
        if (frame) {
          frame.src = frame.dataset.src;
          frame.removeAttribute("data-src");
        }
      }, {once: true});
      items.append(details);
    }
    group.append(items);
    root.append(group);
  }
})();
