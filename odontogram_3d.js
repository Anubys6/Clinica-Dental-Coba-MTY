/**
 * ODONTOGRAMA 3D ANATÓMICO INTERACTIVO COBÁ DENTAL MTY
 * Modelo tridimensional de cavidad oral (Maxilar + Mandíbula + ATM Articulador Bucal)
 * Permite abrir y cerrar la boca de forma realista, rotar en 360°, hacer zoom y
 * seleccionar cada diente individualmente para diagnóstico y cotización en tiempo real.
 */

(function () {
  'use strict';

  // Metadatos anatómicos FDI Internacional
  const FDI_NAMES = {
    // Cuadrante 1 (Superior Derecho)
    '18': 'Tercer Molar Sup. Der. (Muela del Juicio)',
    '17': 'Segundo Molar Sup. Der.',
    '16': 'Primer Molar Sup. Der. (Molar de los 6 años)',
    '15': 'Segundo Premolar Sup. Der.',
    '14': 'Primer Premolar Sup. Der.',
    '13': 'Canino Sup. Der. (Colmillo)',
    '12': 'Incisivo Lateral Sup. Der.',
    '11': 'Incisivo Central Sup. Der. (Paleta)',
    // Cuadrante 2 (Superior Izquierdo)
    '21': 'Incisivo Central Sup. Izq. (Paleta)',
    '22': 'Incisivo Lateral Sup. Izq.',
    '23': 'Canino Sup. Izq. (Colmillo)',
    '24': 'Primer Premolar Sup. Izq.',
    '25': 'Segundo Premolar Sup. Izq.',
    '26': 'Primer Molar Sup. Izq. (Molar de los 6 años)',
    '27': 'Segundo Molar Sup. Izq.',
    '28': 'Tercer Molar Sup. Izq. (Muela del Juicio)',
    // Cuadrante 3 (Inferior Izquierdo)
    '31': 'Incisivo Central Inf. Izq.',
    '32': 'Incisivo Lateral Inf. Izq.',
    '33': 'Canino Inf. Izq.',
    '34': 'Primer Premolar Inf. Izq.',
    '35': 'Segundo Premolar Inf. Izq.',
    '36': 'Primer Molar Inf. Izq.',
    '37': 'Segundo Molar Inf. Izq.',
    '38': 'Tercer Molar Inf. Izq. (Muela del Juicio)',
    // Cuadrante 4 (Inferior Derecho)
    '41': 'Incisivo Central Inf. Der.',
    '42': 'Incisivo Lateral Inf. Der.',
    '43': 'Canino Inf. Der.',
    '44': 'Primer Premolar Inf. Der.',
    '45': 'Segundo Premolar Inf. Der.',
    '46': 'Primer Molar Inf. Der.',
    '47': 'Segundo Molar Inf. Der.',
    '48': 'Tercer Molar Inf. Der. (Muela del Juicio)',
    // Dentición Infantil (Niño)
    '55': 'Segundo Molar Temporal Sup. Der.',
    '54': 'Primer Molar Temporal Sup. Der.',
    '53': 'Canino Temporal Sup. Der.',
    '52': 'Incisivo Lateral Temporal Sup. Der.',
    '51': 'Incisivo Central Temporal Sup. Der.',
    '61': 'Incisivo Central Temporal Sup. Izq.',
    '62': 'Incisivo Lateral Temporal Sup. Izq.',
    '63': 'Canino Temporal Sup. Izq.',
    '64': 'Primer Molar Temporal Sup. Izq.',
    '65': 'Segundo Molar Temporal Sup. Izq.',
    '71': 'Incisivo Central Temporal Inf. Izq.',
    '72': 'Incisivo Lateral Temporal Inf. Izq.',
    '73': 'Canino Temporal Inf. Izq.',
    '74': 'Primer Molar Temporal Inf. Izq.',
    '75': 'Segundo Molar Temporal Inf. Izq.',
    '81': 'Incisivo Central Temporal Inf. Der.',
    '82': 'Incisivo Lateral Temporal Inf. Der.',
    '83': 'Canino Temporal Inf. Der.',
    '84': 'Primer Molar Temporal Inf. Der.',
    '85': 'Segundo Molar Temporal Inf. Der.'
  };

  class Odontogram3DViewer {
    constructor() {
      this.container = null;
      this.renderer = null;
      this.scene = null;
      this.camera = null;
      this.controls = null;
      this.raycaster = new THREE.Raycaster();
      this.mouse = new THREE.Vector2();

      // Grupos jerárquicos de la boca y articulación mandibular (ATM)
      this.rootGroup = null;
      this.upperJawGroup = null;
      this.mandibleHinge = null;
      this.lowerJawGroup = null;

      // Registro de piezas dentales 3D
      this.toothMeshes = {}; // fdi -> THREE.Mesh
      this.teethData = {};   // fdi -> metadata (isUpper, type, etc.)
      this.activeDentition = 'hombre'; // 'hombre', 'mujer', 'nino'

      // Estados de apertura
      this.mouthOpenFraction = 0.55; // 0.0 cerrada, 1.0 máxima apertura (aprox 35°)
      this.targetOpenFraction = 0.55;
      this.isAutoDemo = false;
      this.demoAngle = 0;

      // Raycast / Hover
      this.hoveredToothFDI = null;
      this.tooltipEl = null;

      // Callbacks
      this.onToothSelectCallback = null;

      // Materiales base cacheados
      this.materialsCache = {};
      this.initMaterials();

      // Audio sintetizado
      this.audioCtx = null;
    }

    init(containerEl, onToothSelect) {
      if (!containerEl) return;
      this.container = containerEl;
      this.onToothSelectCallback = onToothSelect;

      const width = this.container.clientWidth || 800;
      const height = this.container.clientHeight || 520;

      // Escena Three.js
      this.scene = new THREE.Scene();
      this.scene.background = new THREE.Color(0x070B14);

      // Cámara en perspectiva
      this.camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 100);
      this.camera.position.set(0, 2.2, 12.5);

      // Renderer WebGL de alta precisión
      this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
      this.renderer.setSize(width, height);
      this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      this.renderer.shadowMap.enabled = true;
      this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
      this.container.innerHTML = '';
      this.container.appendChild(this.renderer.domElement);

      // OrbitControls para rotación 3D natural y zoom
      if (THREE.OrbitControls) {
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.08;
        this.controls.minDistance = 4.5;
        this.controls.maxDistance = 22.0;
        this.controls.maxPolarAngle = Math.PI / 1.6;
        this.controls.target.set(0, 0, -0.4);
      }

      // Iluminación clínica dental
      this.setupLighting();

      // Construcción del modelo anatómico (Arcada superior + Mandíbula + ATM)
      this.buildOralAnatomy(this.activeDentition);

      // Tooltip HTML flotante HUD
      this.setupHUDTooltip();

      // Listeners de eventos
      this.setupEventListeners();

      // Loop de renderizado 60fps
      this.animate = this.animate.bind(this);
      requestAnimationFrame(this.animate);
    }

    initMaterials() {
      // Esmalte dental natural de alta estética (Vita A1/A2)
      this.materialsCache.enamel = new THREE.MeshStandardMaterial({
        color: 0xFAF8F5,
        roughness: 0.22,
        metalness: 0.05,
        envMapIntensity: 1.2
      });

      // Encía anatómica rosada
      this.materialsCache.gingivaUpper = new THREE.MeshStandardMaterial({
        color: 0xD9727B,
        roughness: 0.55,
        metalness: 0.08
      });
      this.materialsCache.gingivaLower = new THREE.MeshStandardMaterial({
        color: 0xCB6770,
        roughness: 0.55,
        metalness: 0.08
      });

      // Materiales patológicos / de restauración
      this.materialsCache.caries = new THREE.MeshStandardMaterial({
        color: 0x3E1C12,
        roughness: 0.85,
        metalness: 0.1,
        emissive: 0x7F1D1D,
        emissiveIntensity: 0.35
      });

      this.materialsCache.resina = new THREE.MeshStandardMaterial({
        color: 0xE8F4F8,
        roughness: 0.28,
        metalness: 0.08,
        emissive: 0x0284C7,
        emissiveIntensity: 0.35
      });

      this.materialsCache.endodoncia = new THREE.MeshStandardMaterial({
        color: 0xFEF3C7,
        roughness: 0.3,
        metalness: 0.15,
        emissive: 0xD97706,
        emissiveIntensity: 0.5
      });

      this.materialsCache.zirconia = new THREE.MeshStandardMaterial({
        color: 0xFAF5FF,
        roughness: 0.12,
        metalness: 0.35,
        emissive: 0x9333EA,
        emissiveIntensity: 0.4
      });

      this.materialsCache.implante = new THREE.MeshStandardMaterial({
        color: 0x64748B,
        roughness: 0.25,
        metalness: 0.85,
        emissive: 0x059669,
        emissiveIntensity: 0.45
      });

      this.materialsCache.brackets = new THREE.MeshStandardMaterial({
        color: 0xFDF2F8,
        roughness: 0.2,
        metalness: 0.4,
        emissive: 0xDB2777,
        emissiveIntensity: 0.5
      });

      this.materialsCache.extraccion = new THREE.MeshBasicMaterial({
        color: 0x64748B,
        wireframe: true,
        transparent: true,
        opacity: 0.2
      });

      // Material de realce hover (Glow Cyan Cobá)
      this.hoverEmissiveColor = new THREE.Color(0x06B6D4);
    }

    setupLighting() {
      // Luz ambiente suave
      const ambientLight = new THREE.AmbientLight(0xE2E8F0, 0.75);
      this.scene.add(ambientLight);

      // Luz frontal del odontólogo (Lámpara de sillón dental)
      const chairLight = new THREE.DirectionalLight(0xFFFFFF, 1.3);
      chairLight.position.set(0, 8, 10);
      chairLight.castShadow = true;
      this.scene.add(chairLight);

      // Luz cenital focal hacia las caras oclusales
      const oclusalSpot = new THREE.SpotLight(0xF8FAFC, 1.2, 30, Math.PI / 4, 0.4);
      oclusalSpot.position.set(0, 10, 0);
      oclusalSpot.target.position.set(0, 0, 0);
      this.scene.add(oclusalSpot);
      this.scene.add(oclusalSpot.target);

      // Luces de acento estético (Cyan y Azul Cobá Luxury)
      const rimCyan = new THREE.DirectionalLight(0x06B6D4, 0.5);
      rimCyan.position.set(-6, -2, -6);
      this.scene.add(rimCyan);

      const rimBlue = new THREE.DirectionalLight(0x3B82F6, 0.45);
      rimBlue.position.set(6, -2, -6);
      this.scene.add(rimBlue);
    }

    buildOralAnatomy(dentitionType = 'hombre') {
      // Limpiar grupos anteriores si existían
      if (this.rootGroup) {
        this.scene.remove(this.rootGroup);
      }

      this.toothMeshes = {};
      this.teethData = {};
      this.rootGroup = new THREE.Group();
      this.scene.add(this.rootGroup);

      // 1. Arcada Maxilar Superior (Fija o con leve inclinación estática)
      this.upperJawGroup = new THREE.Group();
      this.upperJawGroup.position.set(0, 0.75, 0);
      this.rootGroup.add(this.upperJawGroup);

      // 2. Articulador Mandibular ATM (Hinge pivot en el cóndilo mandibular)
      // La articulación temporomandibular se ubica posteriormente y superior a la arcada
      this.mandibleHinge = new THREE.Group();
      this.mandibleHinge.position.set(0, 0.85, -3.8); // Eje de rotación condilar
      this.rootGroup.add(this.mandibleHinge);

      // 3. Mandíbula Inferior (Hija del Hinge para que gire anatómicamente hacia abajo y atrás)
      this.lowerJawGroup = new THREE.Group();
      this.lowerJawGroup.position.set(0, -1.6, 3.8); // Offset para que coincida con el cóndilo
      this.mandibleHinge.add(this.lowerJawGroup);

      // Crear encías maxilar y mandibular
      this.buildGingivaCurves(dentitionType);

      // Generar piezas dentales acordes a la dentición seleccionada
      if (dentitionType === 'nino') {
        this.buildDeciduousDentition();
      } else {
        this.buildAdultDentition(dentitionType);
      }

      // Aplicar apertura bucal inicial
      this.setMouthOpen(this.mouthOpenFraction);
    }

    buildGingivaCurves(dentitionType) {
      const isChild = (dentitionType === 'nino');
      const scaleX = isChild ? 2.2 : 2.9;
      const scaleZ = isChild ? 2.2 : 3.0;

      // Encía Superior (Arco parabólico maxilar con reborde alveolar)
      const upperPoints = [];
      for (let t = -Math.PI * 0.46; t <= Math.PI * 0.46; t += 0.08) {
        const x = Math.sin(t) * scaleX;
        const z = Math.cos(t) * scaleZ - 1.2;
        upperPoints.push(new THREE.Vector3(x, 0.25, z));
      }
      const upperCurve = new THREE.CatmullRomCurve3(upperPoints);
      const upperGumGeo = new THREE.TubeGeometry(upperCurve, 40, isChild ? 0.42 : 0.52, 12, false);
      const upperGumMesh = new THREE.Mesh(upperGumGeo, this.materialsCache.gingivaUpper);
      upperGumMesh.receiveShadow = true;
      this.upperJawGroup.add(upperGumMesh);

      // Encía Inferior (Arco mandibular ligeramente más cerrado)
      const lowerPoints = [];
      for (let t = -Math.PI * 0.46; t <= Math.PI * 0.46; t += 0.08) {
        const x = Math.sin(t) * (scaleX * 0.94);
        const z = Math.cos(t) * (scaleZ * 0.96) - 1.35;
        lowerPoints.push(new THREE.Vector3(x, -0.25, z));
      }
      const lowerCurve = new THREE.CatmullRomCurve3(lowerPoints);
      const lowerGumGeo = new THREE.TubeGeometry(lowerCurve, 40, isChild ? 0.38 : 0.48, 12, false);
      const lowerGumMesh = new THREE.Mesh(lowerGumGeo, this.materialsCache.gingivaLower);
      lowerGumMesh.receiveShadow = true;
      this.lowerJawGroup.add(lowerGumMesh);
    }

    buildAdultDentition(variant = 'hombre') {
      const isFemale = (variant === 'mujer');
      const scaleFactor = isFemale ? 0.93 : 1.0;

      // 16 Dientes Superiores (FDI 18 a 28)
      const upperFdis = [
        '18','17','16','15','14','13','12','11',
        '21','22','23','24','25','26','27','28'
      ];

      // 16 Dientes Inferiores (FDI 48 a 38)
      const lowerFdis = [
        '48','47','46','45','44','43','42','41',
        '31','32','33','34','35','36','37','38'
      ];

      // Distribución angular a lo largo de la arcada
      const totalTeeth = 16;
      upperFdis.forEach((fdi, index) => {
        // Paramétro u de -1.0 a +1.0
        const u = -1.0 + (index + 0.5) * (2.0 / totalTeeth);
        const pos = this.calcArchPosition(u, true, false);
        const toothType = this.getToothClass(fdi);
        const mesh = this.createAnatomicalToothMesh(fdi, toothType, true, scaleFactor);

        mesh.position.set(pos.x, pos.y, pos.z);
        mesh.rotation.y = pos.angle;
        mesh.rotation.x = 0.08; // Ligera inclinación vestibular maxilar

        this.upperJawGroup.add(mesh);
        this.toothMeshes[fdi] = mesh;
        this.teethData[fdi] = { isUpper: true, fdi: fdi, name: FDI_NAMES[fdi] || `Diente #${fdi}`, state: 'sano' };
      });

      lowerFdis.forEach((fdi, index) => {
        const u = -1.0 + (index + 0.5) * (2.0 / totalTeeth);
        const pos = this.calcArchPosition(u, false, false);
        const toothType = this.getToothClass(fdi);
        const mesh = this.createAnatomicalToothMesh(fdi, toothType, false, scaleFactor);

        mesh.position.set(pos.x, pos.y, pos.z);
        mesh.rotation.y = pos.angle;
        mesh.rotation.x = -0.06; // Ligera inclinación lingual mandibular

        this.lowerJawGroup.add(mesh);
        this.toothMeshes[fdi] = mesh;
        this.teethData[fdi] = { isUpper: false, fdi: fdi, name: FDI_NAMES[fdi] || `Diente #${fdi}`, state: 'sano' };
      });
    }

    buildDeciduousDentition() {
      // 10 Dientes Superiores Temporales
      const upperFdis = ['55','54','53','52','51','61','62','63','64','65'];
      // 10 Dientes Inferiores Temporales
      const lowerFdis = ['85','84','83','82','81','71','72','73','74','75'];

      const totalTeeth = 10;
      upperFdis.forEach((fdi, index) => {
        const u = -0.9 + (index + 0.5) * (1.8 / totalTeeth);
        const pos = this.calcArchPosition(u, true, true);
        const toothType = this.getToothClass(fdi);
        const mesh = this.createAnatomicalToothMesh(fdi, toothType, true, 0.78);

        mesh.position.set(pos.x, pos.y, pos.z);
        mesh.rotation.y = pos.angle;
        this.upperJawGroup.add(mesh);
        this.toothMeshes[fdi] = mesh;
        this.teethData[fdi] = { isUpper: true, fdi: fdi, name: FDI_NAMES[fdi] || `Diente Temporal #${fdi}`, state: 'sano' };
      });

      lowerFdis.forEach((fdi, index) => {
        const u = -0.9 + (index + 0.5) * (1.8 / totalTeeth);
        const pos = this.calcArchPosition(u, false, true);
        const toothType = this.getToothClass(fdi);
        const mesh = this.createAnatomicalToothMesh(fdi, toothType, false, 0.78);

        mesh.position.set(pos.x, pos.y, pos.z);
        mesh.rotation.y = pos.angle;
        this.lowerJawGroup.add(mesh);
        this.toothMeshes[fdi] = mesh;
        this.teethData[fdi] = { isUpper: false, fdi: fdi, name: FDI_NAMES[fdi] || `Diente Temporal #${fdi}`, state: 'sano' };
      });
    }

    calcArchPosition(u, isUpper, isChild) {
      // Curva parabólica anatómica
      const maxW = isChild ? 2.1 : (isUpper ? 2.85 : 2.68);
      const maxD = isChild ? 2.0 : (isUpper ? 2.95 : 2.75);

      // Distribución elíptica armónica
      const theta = u * (Math.PI * 0.44);
      const x = Math.sin(theta) * maxW;
      const z = Math.cos(theta) * maxD - (isUpper ? 1.25 : 1.45);
      const y = isUpper ? 0.05 : -0.05;

      // Ángulo normal tangencial para orientar la cara vestibular hacia afuera
      const dx = Math.cos(theta) * maxW;
      const dz = -Math.sin(theta) * maxD;
      const angle = Math.atan2(dx, dz) - Math.PI / 2;

      return { x, y, z, angle };
    }

    getToothClass(fdiStr) {
      const lastDigit = parseInt(fdiStr.slice(-1), 10);
      if (lastDigit === 1) return 'central_incisor';
      if (lastDigit === 2) return 'lateral_incisor';
      if (lastDigit === 3) return 'canine';
      if (lastDigit === 4 || lastDigit === 5) {
        // En temporales 4 y 5 son molares temporales
        return (parseInt(fdiStr, 10) > 50) ? 'molar' : 'premolar';
      }
      return 'molar'; // 6, 7, 8
    }

    createAnatomicalToothMesh(fdi, type, isUpper, scaleFactor = 1.0) {
      const toothGroup = new THREE.Group();
      toothGroup.name = `tooth_${fdi}`;
      toothGroup.userData = { fdi: fdi, isUpper: isUpper, toothType: type };

      let crownGeo;
      const s = scaleFactor;

      if (type === 'molar') {
        // Molar: Corona romboidal robusta con 4 cúspides y tabla oclusal anatómica
        crownGeo = new THREE.CylinderGeometry(0.38 * s, 0.44 * s, 0.62 * s, 8, 2);
        // Modificar vértices oclusales para esculpir cúspides prominentes
        const pos = crownGeo.attributes.position;
        for (let i = 0; i < pos.count; i++) {
          const y = pos.getY(i);
          if (y > 0.15) { // Cúspides
            const x = pos.getX(i);
            const z = pos.getZ(i);
            const dist = Math.sqrt(x * x + z * z);
            if (dist > 0.18) {
              pos.setY(i, y + 0.08 * s); // Cúspides periféricas elevadas
            } else {
              pos.setY(i, y - 0.05 * s); // Fosa central de desarrollo
            }
          }
        }
        crownGeo.computeVertexNormals();

      } else if (type === 'premolar') {
        // Premolar: Corona bicúspidea redondeada
        crownGeo = new THREE.CylinderGeometry(0.28 * s, 0.34 * s, 0.58 * s, 7, 2);
        const pos = crownGeo.attributes.position;
        for (let i = 0; i < pos.count; i++) {
          const y = pos.getY(i);
          if (y > 0.12) {
            const z = pos.getZ(i);
            if (Math.abs(z) > 0.14) {
              pos.setY(i, y + 0.06 * s); // Cúspide vestibular y lingual
            }
          }
        }
        crownGeo.computeVertexNormals();

      } else if (type === 'canine') {
        // Canino: Cúspide piramidal prominente con arista labial
        crownGeo = new THREE.ConeGeometry(0.32 * s, 0.72 * s, 6);
        crownGeo.rotateX(isUpper ? Math.PI : 0);

      } else if (type === 'lateral_incisor') {
        // Incisivo Lateral: Corona delgada espatulada
        crownGeo = new THREE.BoxGeometry(0.32 * s, 0.65 * s, 0.22 * s, 2, 2, 2);

      } else {
        // Incisivo Central: Corona ancha en cincel de alta estética
        crownGeo = new THREE.BoxGeometry(0.42 * s, 0.72 * s, 0.24 * s, 2, 2, 2);
      }

      // Material clonado para permitir coloración individual según diagnóstico
      const toothMat = this.materialsCache.enamel.clone();
      const crownMesh = new THREE.Mesh(crownGeo, toothMat);
      crownMesh.castShadow = true;
      crownMesh.receiveShadow = true;
      crownMesh.userData = { fdi: fdi, isToothRoot: false };

      // Orientar hacia el plano oclusal
      if (isUpper) {
        crownMesh.position.y = -0.15 * s;
      } else {
        crownMesh.position.y = 0.15 * s;
      }
      toothGroup.add(crownMesh);

      // Raíz simulada que penetra en la encía (Visible en caso de implante o extracción)
      const rootGeo = new THREE.ConeGeometry(0.22 * s, 0.65 * s, 5);
      if (!isUpper) rootGeo.rotateX(Math.PI);
      const rootMat = new THREE.MeshStandardMaterial({
        color: 0xE2D9C8,
        roughness: 0.6,
        metalness: 0.05
      });
      const rootMesh = new THREE.Mesh(rootGeo, rootMat);
      rootMesh.position.y = isUpper ? 0.35 * s : -0.35 * s;
      toothGroup.add(rootMesh);

      // Guardar referencia al mesh primario clicable
      crownMesh.parentGroup = toothGroup;
      return toothGroup;
    }

    /**
     * Ajuste de la apertura bucal (Mandibular Hinge Angle)
     * @param {number} fraction 0.0 (Cerrada) a 1.0 (Apertura Máxima ~35°)
     */
    setMouthOpen(fraction) {
      this.mouthOpenFraction = Math.max(0.0, Math.min(1.0, fraction));
      if (this.mandibleHinge) {
        // Rotación en radianes sobre el eje transversal condilar de la ATM
        const maxAngleRad = 0.58; // ~33 grados de apertura fisiológica
        this.mandibleHinge.rotation.x = this.mouthOpenFraction * maxAngleRad;
      }
      // Actualizar slider en UI si existe
      const slider = document.getElementById('odoMouthOpenSlider');
      if (slider && parseFloat(slider.value) !== this.mouthOpenFraction * 100) {
        slider.value = Math.round(this.mouthOpenFraction * 100);
      }
      const valLabel = document.getElementById('odoMouthOpenVal');
      if (valLabel) {
        valLabel.textContent = `${Math.round(this.mouthOpenFraction * 100)}%`;
      }
    }

    animateMouthOpen(targetFraction, durationMs = 600) {
      const startFraction = this.mouthOpenFraction;
      const startTime = performance.now();
      const self = this;

      function step(now) {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / durationMs, 1.0);
        // Easing suave in-out
        const ease = 0.5 - 0.5 * Math.cos(progress * Math.PI);
        self.setMouthOpen(startFraction + (targetFraction - startFraction) * ease);

        if (progress < 1.0) {
          requestAnimationFrame(step);
        }
      }
      requestAnimationFrame(step);
    }

    toggleAutoDemo() {
      this.isAutoDemo = !this.isAutoDemo;
      const btn = document.getElementById('btnOdoAutoDemo');
      if (btn) {
        btn.textContent = this.isAutoDemo ? '⏸️ Pausar Demo' : '🔄 Auto-Apertura Demo';
        btn.classList.toggle('active', this.isAutoDemo);
      }
    }

    setCameraPreset(preset) {
      if (!this.camera || !this.controls) return;

      const duration = 650;
      const startTime = performance.now();
      const startPos = this.camera.position.clone();
      const startTarget = this.controls.target.clone();

      let targetPos = new THREE.Vector3(0, 2.2, 12.5);
      let targetCenter = new THREE.Vector3(0, 0, -0.4);

      if (preset === 'frontal') {
        // Vista frontal directa a la sonrisa
        targetPos.set(0, 0.4, 11.5);
        targetCenter.set(0, 0, 0);
      } else if (preset === 'upper') {
        // Vista oclusal del Maxilar Superior (Mirando desde abajo hacia arriba a los molares sup)
        targetPos.set(0, -7.5, 3.2);
        targetCenter.set(0, 1.2, -0.8);
        this.animateMouthOpen(0.95, 400); // Abrir boca automáticamente para ver las caras oclusales
      } else if (preset === 'lower') {
        // Vista oclusal de la Mandíbula Inferior (Mirando desde arriba hacia abajo a los molares inf)
        targetPos.set(0, 8.2, 3.5);
        targetCenter.set(0, -1.2, -0.5);
        this.animateMouthOpen(0.95, 400);
      } else if (preset === 'lateral') {
        // Vista lateral derecha (Guía canina y relación molar)
        targetPos.set(9.5, 1.2, 3.0);
        targetCenter.set(0, 0, 0);
      }

      const self = this;
      function animateCam(now) {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1.0);
        const ease = 0.5 - 0.5 * Math.cos(progress * Math.PI);

        self.camera.position.lerpVectors(startPos, targetPos, ease);
        self.controls.target.lerpVectors(startTarget, targetCenter, ease);
        self.controls.update();

        if (progress < 1.0) {
          requestAnimationFrame(animateCam);
        }
      }
      requestAnimationFrame(animateCam);
    }

    setToothState(fdi, state) {
      const toothGroup = this.toothMeshes[fdi];
      if (!toothGroup) return;

      if (!this.teethData[fdi]) {
        this.teethData[fdi] = { fdi: fdi, state: 'sano' };
      }
      this.teethData[fdi].state = state;

      // Buscar el mesh de la corona (primer hijo)
      const crown = toothGroup.children[0];
      if (!crown) return;

      // Eliminar aditamentos previos (brackets, poste, etc)
      while (toothGroup.children.length > 2) {
        const extra = toothGroup.children[toothGroup.children.length - 1];
        toothGroup.remove(extra);
      }

      crown.visible = true;

      if (state === 'sano' || !state) {
        crown.material = this.materialsCache.enamel.clone();
      } else if (state === 'caries') {
        crown.material = this.materialsCache.caries.clone();
      } else if (state === 'resina') {
        crown.material = this.materialsCache.resina.clone();
      } else if (state === 'endodoncia') {
        crown.material = this.materialsCache.endodoncia.clone();
      } else if (state === 'zirconia') {
        crown.material = this.materialsCache.zirconia.clone();
      } else if (state === 'implante') {
        crown.material = this.materialsCache.implante.clone();
        // Agregar tornillo de titanio emergente
        const screwGeo = new THREE.CylinderGeometry(0.12, 0.08, 0.7, 8);
        const screwMat = new THREE.MeshStandardMaterial({ color: 0x94A3B8, metalness: 0.9, roughness: 0.2 });
        const screw = new THREE.Mesh(screwGeo, screwMat);
        screw.position.y = this.teethData[fdi].isUpper ? 0.5 : -0.5;
        toothGroup.add(screw);
      } else if (state === 'brackets') {
        crown.material = this.materialsCache.brackets.clone();
        // Agregar aditamento bracket metálico con liga rosa
        const bracketGeo = new THREE.BoxGeometry(0.18, 0.16, 0.1);
        const bracketMat = new THREE.MeshStandardMaterial({ color: 0xCBD5E1, metalness: 0.9, roughness: 0.1 });
        const bracket = new THREE.Mesh(bracketGeo, bracketMat);
        bracket.position.set(0, 0, 0.28);
        toothGroup.add(bracket);
      } else if (state === 'extraccion') {
        crown.material = this.materialsCache.extraccion;
      }
    }

    resetAllTeeth() {
      Object.keys(this.toothMeshes).forEach(fdi => {
        this.setToothState(fdi, 'sano');
      });
    }

    setDentition(type) {
      if (this.activeDentition === type) return;
      this.activeDentition = type;
      this.buildOralAnatomy(type);
    }

    setupHUDTooltip() {
      let el = document.getElementById('odo3DTooltip');
      if (!el) {
        el = document.createElement('div');
        el.id = 'odo3DTooltip';
        el.style.position = 'absolute';
        el.style.display = 'none';
        el.style.pointerEvents = 'none';
        el.style.background = 'rgba(7, 11, 20, 0.92)';
        el.style.backdropFilter = 'blur(10px)';
        el.style.border = '1px solid rgba(6, 182, 212, 0.5)';
        el.style.borderRadius = '8px';
        el.style.padding = '8px 12px';
        el.style.color = '#FFF';
        el.style.fontSize = '12px';
        el.style.fontWeight = '700';
        el.style.boxShadow = '0 8px 25px rgba(0,0,0,0.6), 0 0 15px rgba(6,182,212,0.3)';
        el.style.zIndex = '50';
        el.style.transform = 'translate(-50%, -125%)';
        this.container.style.position = 'relative';
        this.container.appendChild(el);
      }
      this.tooltipEl = el;
    }

    setupEventListeners() {
      const dom = this.renderer.domElement;

      // Detección de movimiento de ratón para Raycast y Hover
      dom.addEventListener('pointermove', (e) => {
        const rect = dom.getBoundingClientRect();
        this.mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

        this.checkRaycastHover(e.clientX - rect.left, e.clientY - rect.top);
      });

      dom.addEventListener('pointerleave', () => {
        this.clearHover();
        if (this.tooltipEl) this.tooltipEl.style.display = 'none';
      });

      // Clic interactivo para seleccionar el diente
      let clickStartX = 0, clickStartY = 0;
      dom.addEventListener('pointerdown', (e) => {
        clickStartX = e.clientX;
        clickStartY = e.clientY;
      });

      dom.addEventListener('pointerup', (e) => {
        const dist = Math.hypot(e.clientX - clickStartX, e.clientY - clickStartY);
        if (dist > 6) return; // Si arrastró para rotar la cámara, ignorar clic

        const intersectedTooth = this.getIntersectedTooth();
        if (intersectedTooth) {
          this.playHapticSound();
          if (this.onToothSelectCallback) {
            this.onToothSelectCallback(intersectedTooth.fdi, intersectedTooth);
          }
        }
      });

      // Redimensionamiento de ventana
      window.addEventListener('resize', () => {
        this.refreshSize();
      });
    }

    getIntersectedTooth() {
      this.raycaster.setFromCamera(this.mouse, this.camera);
      // Colectar todos los meshes de dientes
      const candidates = [];
      Object.values(this.toothMeshes).forEach(group => {
        if (group.children[0]) candidates.push(group.children[0]);
      });

      const intersects = this.raycaster.intersectObjects(candidates, false);
      if (intersects.length > 0) {
        const hit = intersects[0].object;
        const parentGroup = hit.parent;
        if (parentGroup && parentGroup.userData && parentGroup.userData.fdi) {
          const fdi = parentGroup.userData.fdi;
          return {
            fdi: fdi,
            group: parentGroup,
            mesh: hit,
            data: this.teethData[fdi]
          };
        }
      }
      return null;
    }

    checkRaycastHover(screenX, screenY) {
      const hit = this.getIntersectedTooth();

      if (hit) {
        if (this.hoveredToothFDI !== hit.fdi) {
          this.clearHover();
          this.hoveredToothFDI = hit.fdi;
          // Resaltar corona
          if (hit.mesh && hit.mesh.material && hit.mesh.material.emissive) {
            hit.mesh.userData.prevEmissive = hit.mesh.material.emissive.getHex();
            hit.mesh.material.emissive.setHex(0x06B6D4);
            hit.mesh.material.emissiveIntensity = 0.6;
          }
        }

        // Mostrar Tooltip HUD
        if (this.tooltipEl) {
          const info = this.teethData[hit.fdi] || {};
          const statusLabel = (window.ODO_TOOL_META && window.ODO_TOOL_META[info.state]) ?
            window.ODO_TOOL_META[info.state].label : (info.state || 'Sano');

          this.tooltipEl.innerHTML = `
            <div style="display:flex;align-items:center;gap:6px;margin-bottom:3px;">
              <span style="font-size:14px;">🦷</span>
              <strong style="color:var(--cyan);font-size:13px;">Diente #${hit.fdi}</strong>
              <span style="background:rgba(255,255,255,0.1);padding:1px 6px;border-radius:4px;font-size:10px;">${info.isUpper ? 'Maxilar' : 'Mandíbula'}</span>
            </div>
            <div style="font-size:11px;color:#CBD5E1;margin-bottom:4px;">${escapeHtmlText(FDI_NAMES[hit.fdi] || 'Pieza Dental')}</div>
            <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;font-size:10.5px;">
              <span>Estado: <strong>${escapeHtmlText(statusLabel)}</strong></span>
              <span style="color:#FBBF24;">(Clic para marcar)</span>
            </div>
          `;
          this.tooltipEl.style.left = `${screenX}px`;
          this.tooltipEl.style.top = `${screenY}px`;
          this.tooltipEl.style.display = 'block';
        }
        this.container.style.cursor = 'pointer';

      } else {
        this.clearHover();
        if (this.tooltipEl) this.tooltipEl.style.display = 'none';
        this.container.style.cursor = 'grab';
      }
    }

    clearHover() {
      if (this.hoveredToothFDI && this.toothMeshes[this.hoveredToothFDI]) {
        const group = this.toothMeshes[this.hoveredToothFDI];
        const crown = group.children[0];
        if (crown && crown.material && crown.material.emissive) {
          const prev = (crown.userData.prevEmissive !== undefined) ? crown.userData.prevEmissive : 0x000000;
          crown.material.emissive.setHex(prev);
          crown.material.emissiveIntensity = (prev === 0) ? 0 : 0.4;
        }
      }
      this.hoveredToothFDI = null;
    }

    playHapticSound() {
      try {
        if (!this.audioCtx) {
          this.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }
        if (this.audioCtx.state === 'suspended') {
          this.audioCtx.resume();
        }
        const osc = this.audioCtx.createOscillator();
        const gain = this.audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(880, this.audioCtx.currentTime); // A5 nota aguda de precisión médica
        osc.frequency.exponentialRampToValueAtTime(1320, this.audioCtx.currentTime + 0.08);

        gain.gain.setValueAtTime(0.08, this.audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, this.audioCtx.currentTime + 0.09);

        osc.connect(gain);
        gain.connect(this.audioCtx.destination);
        osc.start();
        osc.stop(this.audioCtx.currentTime + 0.09);
      } catch (e) {
        // Audio deshabilitado o bloqueado
      }
    }

    refreshSize() {
      if (!this.container || !this.renderer || !this.camera) return;
      const w = this.container.clientWidth || 800;
      const h = this.container.clientHeight || 520;
      this.camera.aspect = w / h;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(w, h);
    }

    animate(timestamp) {
      requestAnimationFrame(this.animate);

      // Animación suave de apertura automática para demostración
      if (this.isAutoDemo) {
        this.demoAngle += 0.025;
        // Onda senoidal de apertura suave entre 15% y 95%
        const sinVal = (Math.sin(this.demoAngle) + 1.0) / 2.0;
        this.setMouthOpen(0.15 + sinVal * 0.80);
      }

      if (this.controls) {
        this.controls.update();
      }

      this.renderer.render(this.scene, this.camera);
    }
  }

  function escapeHtmlText(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // Exportar al ámbito global
  window.Odontogram3DViewer = Odontogram3DViewer;
  window.odo3DInstance = null;

})();
