# Research areas in English

Рабочий файл английских текстов направлений. Правки отсюда переносятся на сайт командой
`python tools/texts/english.py --import` (собирает `content/english.json`), на сайт он попадет
при следующей сборке (`python tools/build.py`).

Перевод сделан 24.09.2026 по русским текстам из `content/edit/DIRECTIONS_TEXT.md`, вычитывает владелец.
Абзац отделяется пустой строкой, ключевые слова через запятую. Заголовок первого экрана
(`Hero title`) это разметка, как в данных: курсив в `<em>`, перенос `<br>`, строка, которая
не должна переноситься, в `<span class="line">`. В подзаголовке перенос `<br>` ставится там же,
где в русском. Команду здесь не перечисляем, она общая с русской версией, имена и должности
по-английски лежат в `content/edit/EN_PEOPLE.md`.

Ключевых слов у пяти направлений меньше, чем в русском: английские слова длиннее,
и облако вытягивало колонку. Сняты последние в списке, так чтобы пустота между текстом
и приглашением была штатные 60 px на 1920, как у русских страниц.

## Eco-friendly nano- and microtechnology

<!-- id: eco-nano -->

**Hero title:** <em>Eco-friendly</em><br><span class="line">nano- and microtechnology</span>

**Subtitle:** Nanofabrication and plasmonics: nanostructures <br>for ultrasensitive biodiagnostics and sensing

### Text

Large-scale commercial use of nanofabrication methods opens up exciting opportunities for the information technology industry, for complex micro- and nanoelectronic devices, and for nanophotonic and plasmonic devices of many kinds.

Our group specializes in fabricating nanoparticles on thin metal, dielectric and hybrid films. Gold and silver nanoparticles serve as resonant structures in diagnostic applications such as surface-enhanced Raman spectroscopy (SERS) and surface-enhanced fluorescence (SEF) for ultrasensitive detection of biomolecules. In our research we study how plasmonic nanostructures increase the quantum yield.

Besides nanoparticles, we make nanostructures of more complex geometry, including nanoneedles and nanobumps. These structures are also promising for light-sensitive sensors in biomedicine. For example, we have created hybrid nanostructures from silicon–gold thin films that show bright white photoluminescence.

We also have experience in microstructuring the surfaces of titanium, copper, gold, silver, erbium, silicon and other materials. Using optical lithography, or no lithography at all, we modify surfaces and fabricate microfluidic chips.

### Keywords

nanofabrication, plasmonics, SERS, SEF, nanoparticles, hybrid structures, photoluminescence, microstructuring, microfluidic chips, biosensors, optical lithography, surface enhancement, thin films, nanoneedles, nanobumps, laser ablation, quantum yield, white luminescence, silicon–gold, silver

## Unclonable security labels

<!-- id: puf -->

**Hero title:** <em>Unclonable</em> security labels

**Subtitle:** Unique physical security labels <br>that cannot be reproduced or copied

### Text

A physically unclonable label gets its pattern not from a file but from the randomness of laser processing. Even its maker cannot reproduce the pattern, so such a label protects goods and documents better than a printed code. The team covers the whole chain, from the physics of nanostructures and laser printing to recognition and authentication algorithms.

Different physical systems carry the randomness. Resonant silicon nanoparticles produce color through Mie resonances, hybrid gold–silicon structures emit nonlinear white luminescence, and the spread of their nanoscale sizes shows up in the spectrum and works as a key by itself. Silicon–erbium films glow in the telecom infrared range, so the pattern is invisible to the eye. Copper microstructures are laser-reduced directly on flexible polyimide, and such a label withstands water and heating up to 200 °C.

Verification needs no laboratory equipment. The pattern is captured with a microscope or a smartphone with a macro lens, and computer vision compares it with the reference. Hidden security levels come from polarization, as scattering by hybrid nanoantennas changes with the viewing angle, and from an infrared channel for forensic checks. A copy printed at 1200 dpi fails the check.

### Keywords

PUF labels, anti-counterfeiting, nanostructures, laser printing, photoluminescence, Mie resonances, silicon, gold, flexible substrates, computer vision, erbium, optical encoding, hidden labels, hybrid nanoantennas, polarization, IR luminescence, spectral key, copper microstructures, storage density

## Hybrid metal–dielectric nanophotonics

<!-- id: hybrid-nanophotonics -->

**Hero title:** <em>Hybrid</em> metal–dielectric nanophotonics

**Subtitle:** Controlling light at the nanoscale <br>for next-generation optical chips

### Text

Modern devices keep getting smaller and move from electrical to optical signal processing, because electronic information processing has reached its fundamental limits. This led to the concept of the integrated optical chip, a multicomponent photonic device on a single substrate. The path from an electronic chip to an optical one is a step-by-step replacement of electronic components with optical counterparts, aiming at new records in the speed of processing and transmitting information and at new ways to store and protect it.

The advances and knowledge gathered while developing the device of the future formed a research field of its own, hybrid nanophotonics. It studies how photons interact with materials whose characteristic sizes range from 1 to 100 nanometers. The idea is to combine the advantages of metals and high-refractive-index materials (dielectrics and semiconductors) in a single nanostructure. This gives more freedom in tuning the properties of optical devices and yields new passive and active components for integrated optical chips.

### Keywords

hybrid nanophotonics, integrated optics, plasmonics, metamaterials, light–matter interaction, nonlinear optics, nanoantennas, photonic crystals, photonic integrated circuit, optical chips

## AI in nanophotonics

<!-- id: ai-nanophotonics -->

**Hero title:** <em>AI</em> in nanophotonics

**Subtitle:** Computer vision and machine learning <br>for nanophotonic security labels and nanostructure analysis

### Text

Our team actively uses computer vision and machine learning in its projects, above all in the work on physically unclonable security labels and on chemical analysis.

Because every physically unclonable label is unique, using them requires protocols that compare one label with another. We develop such protocols for our labels ourselves, based on the Open Computer Vision library. When a label is read with computer vision, the position and color of each nanostructure in it are identified. After reading, an authentication protocol compares the information the user has read from the label with the information in the database.

Analyzing substances with Raman spectroscopy means processing large amounts of spectral data, which can be quite complex because of the variety of molecular bonds in the substances under study. We solve this with machine learning. We have used various methods for classification and regression, such as decision trees, random forests, support vector machines and logistic regression. These methods have made quantitative and qualitative analysis possible with an accuracy above 95 percent and have automated the processing of large data sets.

### Keywords

computer vision, machine learning, unclonable labels, Raman spectroscopy, OpenCV, spectral analysis, data processing, verification protocols, automation, random forest, decision tree, support vector machines, logistic regression, classification, regression

## Integrated nanophotonics

<!-- id: integrated-nanophotonics -->

**Hero title:** <em>Integrated</em><br>nanophotonics

**Subtitle:** Optical chips for ultrafast data <br>transmission without electronic limits

### Text

Modern telecommunication systems transmit information as optical signals over optical fiber. The signals, however, are processed by the electronic components of the system, which have reached their performance limits. This makes it hard to handle the growing volumes of data. By replacing these electronic components with integrated nanophotonic ones and building an optical chip that works on different physical principles, we can overcome these limits. This would increase bandwidth and data transmission speed.

The key element of an optical chip is a nanoscale light source emitting in the visible or infrared range. Efficient technologies are needed to collect, amplify and guide its emission. Conventional ways of making such nanostructures, however, face a number of problems, including the need for cleanrooms and the difficulty of integrating light emitters with nanoscale structures. That is why one of the main scientific challenges in this field is to develop new light-emitting nanostructures and methods that do not rely on traditional approaches such as electron-beam lithography. Our group develops methods and elements of integrated nanophotonics to bring optical chips into practice.

### Keywords

integrated nanophotonics, optical chips, telecommunications, light sources, nanostructures, bandwidth, signal processing, alternative lithography, emitters, infrared range, component integration, optical fiber, nanoscale sources

## Photothermal and regenerative therapy

<!-- id: photothermal -->

**Hero title:** <em>Photothermal</em><br><span class="line">and regenerative therapy</span>

**Subtitle:** Nanomaterials for photothermal therapy, <br>organ regeneration and cancer immunotherapy

### Text

This research area brings together nanomaterials that turn light into heat and deliver drugs precisely to the target site. Such an approach is needed where systemic treatment affects the whole body, as in melanoma, severe liver damage and disorders of immune regulation. The group works at the intersection of chemistry, physics and biology and takes its developments all the way to tests in cells and animals.

The photothermal line is built on plasmonic gold. Gold nanorods carrying peptides that recognize the MC1R receptor accumulate in the tumor, and femtosecond irradiation heats them more strongly than nanosecond irradiation and suppresses melanoma growth by up to 94 percent. Hybrid plasmonic nanodiamonds do the same while also measuring temperature at the nanoscale, so the heating can be seen right during the procedure.

The second half of the work is about immunity and regeneration. Light-responsive polymer carriers with gold nanorods carry a STING agonist and release it on command of an infrared laser, which reprograms tumor macrophages from the M2 phenotype to the antitumor M1 phenotype without systemic inflammation. For the liver, microRNA-200a is delivered in polylactic acid nanoparticles, where it activates the Keap1/Nrf2 signaling pathway, reduces fibrosis and enhances the natural repair of the tissue.

### Keywords

photothermal therapy, plasmonic nanomaterials, gold, polymers, optical heating, immunotherapy, liver regeneration, nanoparticles, targeted delivery, gold nanorods, melanoma, macrophages, STING agonist, microRNA, nanodiamonds, polymer carriers

## Delivery systems for drugs and bioactive compounds

<!-- id: drug-delivery -->

**Hero title:** <span class="line"><em>Delivery systems</em> for drugs</span><br>and bioactive compounds

**Subtitle:** Redox-responsive and lipid <br>nanoplatforms for controlled drug release

### Text

Even the most advanced and effective drugs act not only on diseased but also on healthy tissue, causing severe side effects. This is especially acute in the treatment of cancer, viral and inflammatory diseases. One of the most promising solutions is nanoscale delivery systems that accumulate in the target tissue and release the drug only when a specific signal appears.

Our group develops chemically controlled redox-responsive delivery systems based on trithiocyanuric acid (TTCA), a biocompatible thiol-containing compound with a simple and scalable synthesis. The nano- and microparticles break down at the elevated intracellular glutathione levels typical of tumor and inflamed cells and release the drug selectively, while the start of therapy is set by administering safe acetylcysteine. The platform suits both small-molecule chemotherapy drugs and small RNAs that need protection from degradation, and hybrid carriers with plasmonic nanoparticles combine diagnostics and therapy.

Our second family of platforms is lipid nanoparticles. We work with liposomes, solid lipid nanoparticles, nanostructured lipid carriers and specialized particles for nucleic acid delivery. Unlike synthetic polymer and inorganic carriers, they are assembled from physiologically relevant and pharmacopoeial lipids, the same building blocks that make up cell membranes, and are therefore highly biocompatible. We keep toxic organic solvents to a minimum and prefer safe homogenization and self-assembly in water, so that high encapsulation efficiency goes together with an exceptional safety profile.

### Keywords

redox-responsive systems, targeted delivery, trithiocyanuric acid, nanoparticles, microcapsules, glutathione, acetylcysteine, small RNAs, chemotherapy drugs, biocompatibility, hybrid materials, lipid nanoparticles, drug delivery, liposomes, encapsulation, pharmacopoeial lipids, homogenization, self-assembly, controlled release

## Biosensing and molecular diagnostics

<!-- id: biosensing -->

**Hero title:** <em>Biosensing</em><br><span class="line">and molecular diagnostics</span>

**Subtitle:** Optical sensors, nanomaterials <br>and DNA constructs for fast and accurate diagnostics

### Text

This research area builds compact optical sensors for rapid diagnostics where no laboratory is at hand. They monitor pollution in the environment and in food and detect pathogens and disease markers at the point of care. Sensitivity comes from nanostructures with unusual optics, and the result is read by color or by spectrum, sometimes directly with a smartphone camera.

The first line of work is optical. Surface-enhanced Raman scattering on gold and silver nanostructures catches low concentrations of dyes and antibiotics, and Ag/TiO2 substrates can now be made quickly and in large batches. Colorimetry on resonant dielectric nanostructures tells viruses from bacteria. Printed nanochains detect a virus in a biofluid in 15 minutes with a limit of one plaque-forming unit per microliter, printed nanoarrays recognize bacteria in water, urine and serum without culturing, and a compact chiral metamaterial brings sensitivity down to the femtomolar level.

The second line is about molecular recognition with DNA constructs. A chemiluminescent DNA nanomachine with peroxidase-like activity finds bacterial nucleic acids and detects Staphylococcus aureus in food samples, and functionalizing glass with labeled oligonucleotides makes such sensors reproducible. The same approach works for genetic variants linked to antibiotic resistance and for early markers of sepsis. Since 2018 the group has worked together with the group of Professor Yanlin Song from the Chinese Academy of Sciences, with 10 joint papers so far.

### Keywords

optical sensors, SERS, colorimetry, nanoparticles, dielectric nanostructures, biosensors, diagnostic platforms, DNA constructs, point-of-care, microfluidics, optical detection, molecular recognition, biomarkers, single-nucleotide variants, oligonucleotides, sepsis markers, printed nanochains, chiral metamaterial

## Microfluidic technologies

<!-- id: microfluidics -->

**Hero title:** <em>Microfluidic</em><br>technologies

**Subtitle:** Lab-on-a-chip <br>for biomedicine and nanomaterial synthesis

### Text

Microfluidic technologies are used in biomedical applications and in nanomaterial synthesis because of unique physical phenomena that arise at the microscale and cannot be reached with traditional approaches.

In biomedicine, microfluidic technologies often take the lab-on-a-chip format. This concept minimizes the sample volume, which matters when working with rare biological samples, and speeds up analysis thanks to faster diffusion and shorter distances, so antigens and antibodies bind within minutes. Integrating such devices into mobile and portable modules enables point-of-care diagnostics. Small volumes make it possible to concentrate the analytes right in the detection zone, which increases sensor sensitivity.

In nanomaterial synthesis, microfluidics solves the main problems of traditional synthesis, namely poor reproducibility, the lack of fine control over reaction kinetics and long synthesis times. The microfluidic approach provides control over particle size and monodispersity, complex particle architectures based on the layer-by-layer concept, and scalability achieved by running a large batch of identical microfluidic devices instead of enlarging the reactor.

Our group focuses on applied problems in biomedicine and on the synthesis of nanomaterials for therapy and diagnostics.

### Keywords

microfluidics, lab-on-a-chip, biomedicine, nanomaterial synthesis, diagnostics, antigens and antibodies, monodispersity, reaction kinetics, scalability, layer-by-layer, portable modules, therapy, microdroplets, small volumes, size control, reproducibility, rapid analysis, analyte concentration, rare samples, diffusion rate

## Thermometry in biological objects

<!-- id: bio-thermometry -->

**Hero title:** <em>Thermometry</em><br><span class="line">in biological objects</span>

**Subtitle:** Optical nanothermometry: <br>temperature control inside the cell for safe therapy

### Text

Temperature is an important biomarker that regulates many processes in the body, starting at the cellular level. Temperature changes affect metabolism, gene expression and cell death mechanisms. Local temperature control therefore not only helps explain many cellular processes but also makes it possible to follow the course of a disease or to monitor the effectiveness of therapy.

The main problem of conventional thermometry is that needles and thermocouples are too large for a cell, so at the nanoscale optical thermometry is often used instead. It relies on detecting the temperature-dependent optical response of luminescent nanoparticles. Under laser irradiation they start to glow, and the characteristics of this glow, such as intensity, spectral peak position and fluorescence decay time, change with temperature. By decoding these signals, we can see the temperature inside a cell in real time.

Our group develops methods for precise noninvasive temperature control during photothermal therapy or light-induced delivery of substances into cells. For this we use silicon, silicon–gold and silicon–germanium nanoparticles, germanium oxide nanoparticles, nanodiamonds with nitrogen-vacancy (NV) centers and rare-earth metals. In this way we want to make laser therapy safe, controllable and predictable.

### Keywords

temperature biomarker, optical thermometry, luminescent nanoparticles, photothermal therapy, noninvasive control, silicon nanoparticles, NV centers, rare-earth metals, light-induced delivery, nanothermometry, cellular thermometry, laser therapy, nanodiamonds, decay time
