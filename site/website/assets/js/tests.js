(function () {
  'use strict';

  var FREQ = [
    { label: 'Jamais', value: 0 },
    { label: 'Plusieurs jours', value: 1 },
    { label: 'Plus de la moitié des jours', value: 2 },
    { label: 'Presque tous les jours', value: 3 }
  ];

  var AGREE = [
    { label: 'Tout à fait d’accord', value: 3 },
    { label: 'D’accord', value: 2 },
    { label: 'Pas d’accord', value: 1 },
    { label: 'Pas du tout d’accord', value: 0 }
  ];

  var GREEN = { color: '#1E9E6A', bg: '#E6F6EF', ink: '#0E5F3F' };
  var TEAL = { color: '#0D7B6E', bg: '#E6F4F1', ink: '#06413A' };
  var GOLD = { color: '#C98A16', bg: '#FDF3E0', ink: '#8A5E10' };
  var ORANGE = { color: '#C2611F', bg: '#FBEDE2', ink: '#7E3D12' };
  var RED = { color: '#D64545', bg: '#FDECEA', ink: '#8E2C2C' };

  var SCALES = {
    phq9: {
      id: 'phq9',
      kicker: 'PHQ-9',
      title: 'Humeur et moral',
      max: 27,
      options: FREQ,
      context: 'Au cours des deux dernières semaines, à quelle fréquence avez-vous été gêné(e) par ce problème ?',
      source: 'Patient Health Questionnaire (PHQ-9), Kroenke, Spitzer & Williams, 2001. Échelle libre d’usage.',
      items: [
        'Peu d’intérêt ou peu de plaisir à faire les choses',
        'Vous sentir triste, déprimé(e) ou désespéré(e)',
        'Difficultés à vous endormir, à rester endormi(e), ou au contraire dormir trop',
        'Vous sentir fatigué(e) ou manquer d’énergie',
        'Avoir peu d’appétit, ou au contraire manger beaucoup trop',
        'Avoir une mauvaise opinion de vous-même, avoir le sentiment d’être nul(le) ou d’avoir déçu votre famille',
        'Avoir du mal à vous concentrer, par exemple pour lire ou suivre une conversation',
        'Bouger ou parler si lentement que les autres ont pu le remarquer — ou au contraire être si agité(e) que vous aviez du mal à tenir en place',
        'Penser qu’il vaudrait mieux mourir, ou envisager de vous faire du mal d’une manière ou d’une autre'
      ],
      bands: [
        {
          min: 0, max: 4, label: 'Aucun signe ou signes minimes', theme: GREEN,
          text: [
            'Sur les deux dernières semaines, vos réponses ne montrent pas de signe marqué de dépression.',
            'Ce résultat ne dit rien du reste de votre vie : il porte sur quinze jours. Si quelque chose vous préoccupe malgré tout, cette préoccupation compte.'
          ],
          cta: 'Refaire le point de temps en temps'
        },
        {
          min: 5, max: 9, label: 'Signes légers', theme: TEAL,
          text: [
            'Quelques signes sont présents, mais ils restent faibles. Cela reflète souvent une période chargée, de la fatigue, un deuil ou un changement de vie.',
            'Refaites le test dans deux semaines. Si le score monte, ou si votre sommeil, votre travail ou vos relations en souffrent, parlez-en à un professionnel.'
          ],
          cta: 'Ne pas laisser s’installer'
        },
        {
          min: 10, max: 14, label: 'Signes modérés', theme: GOLD,
          text: [
            'À partir de ce score, les cliniciens envisagent en général un accompagnement. Ce que vous ressentez est réel : ce n’est ni « dans votre tête », ni un manque de volonté.',
            'Un premier entretien avec un psychologue permet de distinguer une période difficile d’un problème qui demande un suivi. Ce n’est pas un engagement à vie.'
          ],
          cta: 'Parler à un psychologue'
        },
        {
          min: 15, max: 19, label: 'Signes modérément sévères', theme: ORANGE,
          text: [
            'Vos réponses décrivent une souffrance nette, présente depuis deux semaines. Tenir le quotidien à ce niveau demande beaucoup d’énergie, souvent plus que ce que votre entourage imagine.',
            'Consulter un professionnel est vivement recommandé, assez vite. Une dépression se soigne, et plus tôt on s’y prend, mieux c’est.'
          ],
          cta: 'Consulter rapidement'
        },
        {
          min: 20, max: 27, label: 'Signes sévères', theme: RED,
          text: [
            'Vos réponses montrent une souffrance importante sur presque tous les points du questionnaire. Ce résultat doit être pris au sérieux, dès aujourd’hui.',
            'Ne restez pas seul(e) avec ça. Parlez-en à un professionnel et, si possible, à une personne de confiance aujourd’hui. Il existe des traitements qui marchent.'
          ],
          cta: 'Consulter un professionnel maintenant'
        }
      ]
    },

    gad7: {
      id: 'gad7',
      kicker: 'GAD-7',
      title: 'Anxiété et inquiétude',
      max: 21,
      options: FREQ,
      context: 'Au cours des deux dernières semaines, à quelle fréquence avez-vous été gêné(e) par ce problème ?',
      source: 'Generalized Anxiety Disorder scale (GAD-7), Spitzer, Kroenke, Williams & Löwe, 2006. Échelle libre d’usage.',
      items: [
        'Vous sentir nerveux(se), anxieux(se) ou très tendu(e)',
        'Être incapable d’arrêter de vous inquiéter ou de contrôler vos inquiétudes',
        'Vous inquiéter excessivement à propos de tout et de rien',
        'Avoir du mal à vous détendre',
        'Être si agité(e) qu’il est difficile de rester tranquille',
        'Devenir facilement contrarié(e) ou irritable',
        'Avoir peur que quelque chose d’épouvantable puisse arriver'
      ],
      bands: [
        {
          min: 0, max: 4, label: 'Anxiété minime', theme: GREEN,
          text: [
            'Vos réponses ne montrent pas d’anxiété problématique sur les deux dernières semaines.',
            'Un peu d’inquiétude est normale, et même utile : elle nous fait réviser avant un examen ou regarder avant de traverser. Elle devient un sujet quand elle tourne en boucle sans aider à agir.'
          ],
          cta: 'Garder un œil dessus'
        },
        {
          min: 5, max: 9, label: 'Anxiété légère', theme: TEAL,
          text: [
            'Une anxiété est présente. Elle reste supportable mais se remarque : du mal à décrocher, une tension de fond, un sommeil plus léger.',
            'C’est un bon moment pour agir, justement parce que ce n’est pas encore lourd. Quelques séances suffisent souvent à défaire un mécanisme d’inquiétude avant qu’il s’installe.'
          ],
          cta: 'Agir avant que ça monte'
        },
        {
          min: 10, max: 14, label: 'Anxiété modérée', theme: GOLD,
          text: [
            'Vous êtes au-dessus du seuil généralement retenu pour un trouble anxieux. L’inquiétude ne se déclenche plus seulement devant un vrai problème : elle tourne d’elle-même.',
            'Dans ce cas, un accompagnement donne souvent des résultats assez rapides. Un professionnel peut vous proposer des outils concrets, en plus de l’écoute.'
          ],
          cta: 'Parler à un professionnel'
        },
        {
          min: 15, max: 21, label: 'Anxiété sévère', theme: RED,
          text: [
            'Vos réponses décrivent une anxiété intense, presque permanente. À ce niveau, elle use beaucoup d’énergie et gagne le sommeil, le corps, la concentration et les relations.',
            'Consulter est vivement recommandé, sans attendre que ça passe seul. Une anxiété sévère répond bien à une prise en charge, alors que l’attente l’entretient.'
          ],
          cta: 'Consulter rapidement'
        }
      ]
    },

    rses: {
      id: 'rses',
      kicker: 'Échelle de Rosenberg',
      title: 'Estime de soi',
      max: 30,
      options: AGREE,
      context: 'Indiquez à quel point vous êtes d’accord avec cette affirmation.',
      source: 'Rosenberg Self-Esteem Scale (RSES), Morris Rosenberg, 1965. Échelle libre d’usage à des fins éducatives et de recherche.',
      items: [
        { text: 'Je pense que je suis une personne de valeur, au moins autant que les autres.' },
        { text: 'Je pense que je possède un certain nombre de belles qualités.' },
        { text: 'Tout bien considéré, je suis porté(e) à me considérer comme un(e) raté(e).', reverse: true },
        { text: 'Je suis capable de faire les choses aussi bien que la majorité des gens.' },
        { text: 'Je sens peu de raisons d’être fier(ère) de moi.', reverse: true },
        { text: 'J’ai une attitude positive vis-à-vis de moi-même.' },
        { text: 'Dans l’ensemble, je suis satisfait(e) de moi.' },
        { text: 'J’aimerais avoir plus de respect pour moi-même.', reverse: true },
        { text: 'Parfois je me sens vraiment inutile.', reverse: true },
        { text: 'Il m’arrive de penser que je suis un(e) bon(ne) à rien.', reverse: true }
      ],
      bands: [
        {
          min: 0, max: 14, label: 'Estime de soi basse', theme: ORANGE,
          text: [
            'Vous vous jugez sévèrement, sans doute plus que vous ne jugeriez quelqu’un d’autre dans la même situation.',
            'L’estime de soi n’est pas fixée une fois pour toutes. Elle se construit, souvent à partir de ce qu’on nous a renvoyé très tôt, et elle peut se retravailler. Un accompagnement psychologique aide beaucoup sur ce terrain.'
          ],
          cta: 'En parler à un psychologue'
        },
        {
          min: 15, max: 25, label: 'Estime de soi dans la moyenne', theme: TEAL,
          text: [
            'Votre score est dans la fourchette la plus courante. Vous vous reconnaissez des qualités et gardez des zones de doute, ce qui est très répandu.',
            'Si certaines phrases vous ont fait réagir plus que d’autres, regardez-les de plus près. Ce sont souvent les réponses une par une, plus que le score total, qui sont les plus utiles.'
          ],
          cta: 'Regarder les points qui accrochent'
        },
        {
          min: 26, max: 30, label: 'Estime de soi élevée', theme: GREEN,
          text: [
            'Vous vous accordez de la valeur et vous vous reconnaissez des compétences. C’est une vraie ressource dans les périodes difficiles.',
            'Une estime de soi élevée ne protège pas de l’anxiété ni d’un moral en baisse : ce sont d’autres dimensions. Si quelque chose vous pèse, les deux autres tests peuvent aider à y voir plus clair.'
          ],
          cta: 'Essayer les autres tests'
        }
      ]
    }
  };

  var hub = document.getElementById('hub');
  var runner = document.getElementById('runner');
  var resultSection = document.getElementById('result');
  var qFrame = document.getElementById('qFrame');
  var qCount = document.getElementById('qCount');
  var qProgress = document.getElementById('qProgress');
  var btnBack = document.getElementById('btnBack');
  var resultBody = document.getElementById('resultBody');

  var state = null;

  function itemText(item) {
    return typeof item === 'string' ? item : item.text;
  }

  function isReverse(item) {
    return typeof item === 'object' && item.reverse === true;
  }

  function bandFor(scale, score) {
    for (var i = 0; i < scale.bands.length; i++) {
      if (score >= scale.bands[i].min && score <= scale.bands[i].max) return scale.bands[i];
    }
    return scale.bands[scale.bands.length - 1];
  }

  function scoreOf(scale, answers) {
    var total = 0;
    for (var i = 0; i < scale.items.length; i++) {
      var raw = answers[i];
      if (raw === null || raw === undefined) continue;
      total += isReverse(scale.items[i]) ? (3 - raw) : raw;
    }
    return total;
  }

  function show(section) {
    [hub, runner, resultSection].forEach(function (s) {
      s.classList.toggle('is-hidden', s !== section);
    });
  }

  function start(scale) {
    state = { scale: scale, index: 0, answers: new Array(scale.items.length).fill(null) };
    show(runner);
    renderQuestion();
    window.scrollTo({ top: 0, behavior: 'auto' });
  }

  function renderQuestion() {
    var scale = state.scale;
    var i = state.index;
    var total = scale.items.length;

    qCount.textContent = 'Question ' + (i + 1) + ' sur ' + total;
    qProgress.style.width = ((i / total) * 100) + '%';
    btnBack.textContent = i === 0 ? '← Tous les tests' : '← Question précédente';

    var html = '<div class="fade-in">';
    html += '<div class="q-context">' + scale.kicker + ' · ' + scale.context + '</div>';
    html += '<div class="q-text">' + itemText(scale.items[i]) + '</div>';
    html += '<div class="choices">';
    scale.options.forEach(function (opt, k) {
      var picked = state.answers[i] === opt.value ? ' is-picked' : '';
      html += '<button type="button" class="choice' + picked + '" data-value="' + opt.value + '">' +
        '<span class="mark"></span><span>' + opt.label + '</span><kbd>' + (k + 1) + '</kbd></button>';
    });
    html += '</div></div>';

    qFrame.innerHTML = html;

    Array.prototype.forEach.call(qFrame.querySelectorAll('.choice'), function (btn) {
      btn.addEventListener('click', function () {
        answer(parseInt(btn.getAttribute('data-value'), 10));
      });
    });
  }

  function answer(value) {
    state.answers[state.index] = value;
    if (state.index < state.scale.items.length - 1) {
      state.index += 1;
      renderQuestion();
    } else {
      qProgress.style.width = '100%';
      renderResult();
    }
  }

  function goBack() {
    if (!state) return;
    if (state.index === 0) {
      state = null;
      location.hash = '';
      show(hub);
      window.scrollTo({ top: 0, behavior: 'auto' });
      return;
    }
    state.index -= 1;
    renderQuestion();
  }

  function gaugeHtml(scale, score) {
    var span = scale.max + 1;
    var track = '';
    scale.bands.forEach(function (b) {
      var w = ((b.max - b.min + 1) / span) * 100;
      track += '<i style="width:' + w + '%;background:' + b.theme.color + '"></i>';
    });
    var pos = ((score + 0.5) / span) * 100;
    return '<div class="gauge">' +
      '<div class="gauge-track">' + track + '</div>' +
      '<div class="gauge-cursor"><b style="left:' + pos + '%"></b></div>' +
      '<div class="gauge-labels"><span>0</span><span>' + scale.max + '</span></div>' +
      '</div>';
  }

  function crisisHtml() {
    return '<div class="crisis">' +
      '<h4>Une réponse qui compte</h4>' +
      '<p>Vous avez répondu avoir eu des pensées de mort ou l’envie de vous faire du mal. Même si c’est rare, c’est une raison suffisante d’en parler à quelqu’un aujourd’hui.</p>' +
      '<p style="margin-top:12px">Si le danger est immédiat, appelez le <strong>SAMU au 1515</strong> ou les <strong>sapeurs-pompiers au 18</strong>. Vous pouvez aussi joindre directement l’<strong>hôpital psychiatrique de Thiaroye au 33 834 01 58</strong> ou le <strong>service de psychiatrie du CHNU Fann au 33 869 18 18</strong>. Si vous le pouvez, dites-le dès maintenant à une personne de confiance.</p>' +
      '<div class="emergency-nums">' +
      '<a href="tel:1515">Appeler le 1515</a>' +
      '<a href="tel:18">Appeler le 18</a>' +
      '<a href="tel:+221338340158">Thiaroye · 33 834 01 58</a>' +
      '</div></div>';
  }

  function renderResult() {
    var scale = state.scale;
    var score = scoreOf(scale, state.answers);
    var band = bandFor(scale, score);
    var crisis = scale.id === 'phq9' && state.answers[8] > 0;

    var html = '<div class="fade-in">';
    html += '<div class="eyebrow">' + scale.kicker + ' · votre résultat</div>';
    html += '<div class="score-block">';
    html += '<div class="score-head">' +
      '<span class="score-num" style="color:' + band.theme.color + '">' + score + '</span>' +
      '<span class="score-max">sur ' + scale.max + '</span>' +
      '<span class="score-band" style="background:' + band.theme.bg + ';color:' + band.theme.ink + '">' + band.label + '</span>' +
      '</div>';
    html += gaugeHtml(scale, score);
    html += '</div>';

    html += '<h2>Ce que cela veut dire</h2>';
    band.text.forEach(function (p) { html += '<p>' + p + '</p>'; });

    if (crisis) html += crisisHtml();

    html += '<div class="limits">' +
      '<h4>Ce que ce score ne dit pas</h4>' +
      '<p>Ce questionnaire ne connaît ni votre histoire, ni votre contexte, ni ce que vous avez traversé cette semaine. Il ne pose aucun diagnostic et ne remplace pas l’évaluation d’un professionnel, qui seul peut distinguer une réaction normale à une situation difficile d’un trouble. Voyez ce chiffre comme un point de départ pour en parler.</p>' +
      '</div>';

    html += '<div class="next-step">' +
      '<h3>' + band.cta + '</h3>' +
      '<p>PsyConnect est un projet en cours de développement et l’application n’est pas encore ouverte. En attendant, parlez-en à votre médecin ou à un psychologue près de chez vous.</p>' +
      '<div class="row">' +
      '<a class="btn btn--gold" href="index.html#application">Découvrir le projet</a>' +
      '<a class="btn btn--onteal" href="index.html#faq">Questions fréquentes</a>' +
      '</div></div>';

    html += '<div class="result-actions">' +
      '<button class="btn btn--ghost" type="button" id="btnRetry">Refaire ce test</button>' +
      '<button class="btn btn--ghost" type="button" id="btnHub">Voir les autres tests</button>' +
      '</div>';

    html += '<p class="source-line">' + scale.source + ' Traduction française à usage informatif.</p>';
    html += '</div>';

    resultBody.innerHTML = html;
    show(resultSection);
    window.scrollTo({ top: 0, behavior: 'auto' });

    document.getElementById('btnRetry').addEventListener('click', function () { start(scale); });
    document.getElementById('btnHub').addEventListener('click', function () {
      state = null;
      location.hash = '';
      show(hub);
      window.scrollTo({ top: 0, behavior: 'auto' });
    });
  }

  function route() {
    var id = location.hash.replace('#', '');
    if (SCALES[id]) {
      start(SCALES[id]);
    } else {
      state = null;
      show(hub);
    }
  }

  btnBack.addEventListener('click', goBack);

  document.addEventListener('keydown', function (e) {
    if (!state || runner.classList.contains('is-hidden')) return;
    var n = parseInt(e.key, 10);
    if (n >= 1 && n <= state.scale.options.length) {
      e.preventDefault();
      answer(state.scale.options[n - 1].value);
    } else if (e.key === 'Backspace' || e.key === 'ArrowLeft') {
      e.preventDefault();
      goBack();
    }
  });

  window.addEventListener('hashchange', route);
  route();
})();
