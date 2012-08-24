(function() {
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };
  $(document).ready(function() {
    var Animal, AnimalListViewModel, AnimalObservation, Category, Enrichment, EnrichmentListViewModel, EnrichmentNote, Exhibit, HousingGroup, MAX_SCROLLER_ROWS, Observation, ObservationListViewModel, PawsViewModel, Species, Staff, StaffListViewModel, Subcategory, pad, resizeAllCarousels, resizeCarousel, updateAnimalObservation;
    if (!Date.prototype.toISOString) {
      pad = function(number) {
        var r;
        r = String(number);
        if (r.length === 1) {
          r = "0" + r;
        }
        return r;
      };
      Date.prototype.toISOString = function() {
        this.getUTCFullYear() + "-" + pad(this.getUTCMonth() + 1) + "-";
        +pad(this.getUTCDate()) + "T" + pad(this.getUTCHours()) + ":";
        +pad(this.getUTCMinutes()) + ":" + pad(this.getUTCSeconds()) + ".";
        return +String((this.getUTCMilliseconds() / 1000).toFixed(3)).slice(2, 5) + "Z";
      };
    }
    updateAnimalObservation = new ko.subscribable();
    Animal = (function() {
      function Animal(data) {
        this.name = ko.observable(data.name);
        this.id = ko.observable(data.id);
        this.speciesCommonName = ko.observable(data.species.common_name);
        this.speciesId = ko.observable(data.species.id);
        this.speciesScientificName = ko.observable(data.species.scientific_name);
        this.active = ko.observable(false);
        this.observation = ko.observable(null);
      }
      return Animal;
    })();
    AnimalObservation = (function() {
      function AnimalObservation(data) {
        if (data == null) {
          data = null;
        }
        if (data != null) {
          this.id = data.id;
          this.animal = ko.observable(new Animal(data.animal));
          this.observation_id = ko.observable(data.observation.id);
          this.interaction_time = ko.observable(data.interaction_time);
          this.observation_time = ko.observable(data.observation_time);
          this.indirect_use = ko.observable(data.indirect_use);
          this.behavior = ko.observable(data.behavior);
          this.interaction_time.subscribe(__bind(function(value) {
            var d;
            console.log("change interaction_time");
            d = {
              id: this.id,
              value: value,
              type: "interaction_time"
            };
            console.log(d);
            return updateAnimalObservation.notifySubscribers(d, "saveAnimalObservation");
          }, this));
          this.observation_time.subscribe(__bind(function(value) {
            var d;
            console.log("change observation_time");
            d = {
              id: this.id,
              value: value,
              type: "observation_time"
            };
            console.log(d);
            return updateAnimalObservation.notifySubscribers(d, "saveAnimalObservation");
          }, this));
          this.indirect_use.subscribe(__bind(function(value) {
            var d;
            console.log("change indirect_use");
            d = {
              id: this.id,
              value: value,
              type: "indirect_use"
            };
            console.log(d);
            return updateAnimalObservation.notifySubscribers(d, "saveAnimalObservation");
          }, this));
        } else {
          this.id = ko.observable(null);
          this.animal = ko.observable(null);
          this.observation_id = ko.observable(null);
          this.interaction_time = ko.observable(null);
          this.observation_time = ko.observable(null);
          this.indirect_use = ko.observable(null);
          this.behavior = ko.observable(null);
        }
      }
      return AnimalObservation;
    })();
    Exhibit = (function() {
      function Exhibit(data) {
        this.code = ko.observable(data.code);
        this.housingGroups = ko.observableArray($.map(data.housing_groups, function(item) {
          return new HousingGroup(item);
        }));
        this.fullName = ko.computed(__bind(function() {
          return 'Exhibit ' + this.code();
        }, this));
        this.numOwned = ko.computed(__bind(function() {
          var num;
          num = 0;
          $.each(this.housingGroups(), __bind(function(index, val) {
            if (val.isInStaff()) {
              return num++;
            }
          }, this));
          return num;
        }, this));
        this.resourceURI = data.resource_uri;
      }
      return Exhibit;
    })();
    HousingGroup = (function() {
      function HousingGroup(data) {
        if (data != null) {
          this.id = ko.observable(data.id);
          this.name = ko.observable(data.name);
          this.staff = ko.observableArray(data.staff);
          this.resourceURI = data.resource_uri;
          this.animals = ko.observableArray($.map(data.animals, function(item) {
            return new Animal(item);
          }));
        } else {
          this.id = ko.observable(null);
          this.name = ko.observable(null);
          this.staff = ko.observableArray(null);
          this.resourceURI = null;
          this.animals = ko.observableArray(null);
        }
        this.isInStaff = ko.computed(__bind(function() {
          if (this.staff() != null) {
            return this.staff.indexOf('/api/v1/staff/' + window.userId + '/') !== -1;
          } else {
            return false;
          }
        }, this));
      }
      return HousingGroup;
    })();
    Category = (function() {
      function Category(data) {
        if (data == null) {
          data = {};
        }
        this.name = ko.observable(data.name);
        this.id = ko.observable(data.id);
      }
      return Category;
    })();
    Enrichment = (function() {
      function Enrichment(data) {
        if (data != null) {
          this.id = ko.observable(data.id);
          this.name = ko.observable(data.name);
          this.categoryId = ko.observable(data.subcategory.category.id);
          this.categoryName = ko.observable(data.subcategory.category.name);
          this.subcategoryId = ko.observable(data.subcategory.id);
          this.subcategoryName = ko.observable(data.subcategory.name);
          this.count = ko.observable(0);
          this.disabled = false;
        } else {
          this.id = ko.observable(null);
          this.name = ko.observable(null);
          this.categoryId = ko.observable(null);
          this.categoryName = ko.observable(null);
          this.subcategoryId = ko.observable(null);
          this.subcategoryName = ko.observable(null);
          this.count = ko.observable(0);
          this.disabled = false;
        }
      }
      return Enrichment;
    })();
    EnrichmentNote = (function() {
      function EnrichmentNote(data) {
        if (data != null) {
          this.enrichmentId = ko.observable(data.enrichment.id);
          this.speciesCommonName = ko.observable(data.species.common_name);
          this.speciesId = ko.observable(data.species.id);
          this.speciesScientificName = ko.observable(data.species.scientific_name);
          this.species = ko.observable(new Species(data.species));
          this.limitations = ko.observable(data.limitations);
          this.instructions = ko.observable(data.instructions);
        } else {
          this.enrichmentId = ko.observable(null);
          this.speciesCommonName = ko.observable(null);
          this.speciesId = ko.observable(null);
          this.speciesScientificName = ko.observable(null);
          this.species = ko.observable(new Species(null));
          this.limitations = ko.observable(null);
          this.instructions = ko.observable(null);
        }
      }
      return EnrichmentNote;
    })();
    Observation = (function() {
      function Observation(data) {
        if (data == null) {
          data = null;
        }
        if (data != null) {
          this.id = data.id;
          this.enrichment = ko.observable(data.enrichment);
          this.animal_observations = ko.observableArray($.map(data.animal_observations, function(item) {
            return new AnimalObservation(item);
          }));
          this.date_created = ko.observable(data.date_created);
          this.date_finished = ko.observable(data.date_finished);
        } else {
          this.id = null;
          this.enrichment = ko.observable(null);
          this.animal_observations = ko.observableArray([]);
          this.date_created = ko.observable(null);
          this.date_finished = ko.observable(null);
        }
      }
      Observation.prototype.modalTitle = function() {
        var length, pluralized;
        length = this.animal_observations().length;
        pluralized = length > 1 ? ' animals' : ' animal';
        return 'Observing ' + length + pluralized;
      };
      return Observation;
    })();
    Staff = (function() {
      function Staff(data) {
        this.id = ko.observable(data.id);
        this.first_name = ko.observable(data.user.first_name);
        this.last_name = ko.observable(data.user.last_name);
        this.username = ko.observable(data.user.username);
        this.full_name = ko.computed(__bind(function() {
          return this.first_name() + ' ' + this.last_name();
        }, this));
        this.animal_title = ko.computed(__bind(function() {
          return this.full_name() + '\'s animals';
        }, this));
        this.housingGroups = ko.observableArray([]);
        this.loading = ko.observable(false);
        this.is_superuser = ko.observable(data.user.is_superuser);
      }
      Staff.prototype.loadInfo = function() {
        if (this.housingGroups().length !== 0) {
          return;
        }
        this.loading(true);
        return $.getJSON('/api/v1/housingGroup/?format=json&staff_id=' + this.id(), __bind(function(data) {
          var mapped;
          mapped = $.map(data.objects, function(item) {
            return new HousingGroup(item);
          });
          this.housingGroups(mapped);
          return this.loading(false);
        }, this));
      };
      return Staff;
    })();
    Species = (function() {
      function Species(data) {
        if (data != null) {
          this.commonName = ko.observable(data.common_name);
          this.scientificName = ko.observable(data.scientific_name);
          this.id = ko.observable(data.id);
          this.resourceURI = data.resource_uri;
        } else {
          this.commonName = ko.observable(null);
          this.scientificName = ko.observable(null);
          this.id = ko.observable(null);
        }
      }
      return Species;
    })();
    Subcategory = (function() {
      function Subcategory(data) {
        if (data != null) {
          this.name = ko.observable(data.name);
          this.id = ko.observable(data.id);
          this.categoryId = ko.observable(data.category.id);
        } else {
          this.name = ko.observable('');
          this.id = ko.observable('');
          this.categoryId = ko.observable('');
        }
        this.count = ko.observable(0);
      }
      return Subcategory;
    })();
    AnimalListViewModel = (function() {
      function AnimalListViewModel() {
        this.empty = __bind(this.empty, this);
        this.createAnimalObservation = __bind(this.createAnimalObservation, this);
        this.createObservation = __bind(this.createObservation, this);
        this.loadEnrichments = __bind(this.loadEnrichments, this);
        this.idInArray = __bind(this.idInArray, this);
        this.load = __bind(this.load, this);
        this.selectEnrichment = __bind(this.selectEnrichment, this);
        this.newObservation = __bind(this.newObservation, this);
        this.selectHousingGroup = __bind(this.selectHousingGroup, this);
        this.selectExhibit = __bind(this.selectExhibit, this);
        this.toggleAnimal = __bind(this.toggleAnimal, this);
        this.deselectAnimal = __bind(this.deselectAnimal, this);
        this.selectAnimal = __bind(this.selectAnimal, this);
        this.isSelected = __bind(this.isSelected, this);
        this.setCurrentSpecies = __bind(this.setCurrentSpecies, this);
        this.filterSubcategory = __bind(this.filterSubcategory, this);
        this.filterCategory = __bind(this.filterCategory, this);
        this.toggleViewAll = __bind(this.toggleViewAll, this);
        this.createNewAnimal = __bind(this.createNewAnimal, this);
        this.createNewHousingGroup = __bind(this.createNewHousingGroup, this);
        this.createNewExhibit = __bind(this.createNewExhibit, this);
        this.createNewSpecies = __bind(this.createNewSpecies, this);
        var self;
        this.animals = ko.observableArray([]);
        this.species = ko.observableArray([]);
        this.exhibits = ko.observableArray([]);
        this.categories = ko.observableArray([]);
        this.subcategories = ko.observableArray([]);
        this.enrichments = ko.observableArray([]);
        this.enrichmentNotes = ko.observableArray([]);
        this.currentSpecies = ko.observable('');
        this.currentEnrichment = ko.observable(null);
        this.newObservationAjaxLoad = ko.observable(false);
        this.newObservationError = ko.observable(null);
        this.newObservationIsCreating = ko.observable(false);
        this.newObservationSuccess = ko.observable(false);
        this.newAnimalObservationAjaxLoad = ko.observable(false);
        this.newAnimalObservationError = ko.observable(null);
        this.newAnimalObservationIsCreating = ko.observable(false);
        this.newAnimalObservationSuccess = ko.observable(false);
        this.staffs = ko.observableArray([]);
        this.viewAll = ko.observable(false);
        this.viewText = ko.computed(__bind(function() {
          if (this.viewAll()) {
            return 'All Animals';
          } else {
            return 'Your Animals';
          }
        }, this));
        this.filterAnimalsBySpecies = ko.computed(__bind(function() {
          var species;
          species = this.currentSpecies();
          if (species === '') {
            return this.animals();
          }
          return ko.utils.arrayFilter(this.animals(), function(animal) {
            return animal.speciesId() === species.id();
          });
        }, this));
        this.selectedAnimals = ko.observableArray([]);
        this.selectedAnimalsChanged = false;
        this.modalTitleEnrichment = ko.computed(__bind(function() {
          var length, pluralized;
          length = this.selectedAnimals().length;
          pluralized = length !== 1 ? ' animals' : ' animal';
          return 'Select Enrichment - Observing ' + length + pluralized;
        }, this));
        this.modalTitleAnimal = ko.computed(__bind(function() {
          var enrichName, length, pluralized;
          length = this.selectedAnimals().length;
          pluralized = length !== 1 ? ' animals' : ' animal';
          enrichName = this.currentEnrichment() != null ? this.currentEnrichment().name() + ' - ' : '';
          return enrichName + 'Observing ' + length + pluralized;
        }, this));
        this.observation = ko.observable(new Observation());
        this.categoryFilter = ko.observable('');
        this.subcategoryFilter = ko.observable('');
        this.behaviorType = [
          {
            id: -2,
            type: 'Avoid'
          }, {
            id: -1,
            type: 'Negative'
          }, {
            id: 0,
            type: 'N/A'
          }, {
            id: 1,
            type: 'Positive'
          }
        ];
        this.subcategoriesFilterCategory = ko.computed(__bind(function() {
          var category;
          category = this.categoryFilter();
          if (category === '') {
            return [];
          }
          return ko.utils.arrayFilter(this.subcategories(), function(subcategory) {
            return subcategory.categoryId() === category.id();
          });
        }, this));
        this.enrichmentsFilterCategory = ko.computed(__bind(function() {
          var category;
          category = this.categoryFilter();
          if (category === '') {
            return this.enrichments();
          }
          return ko.utils.arrayFilter(this.enrichments(), function(enrichment) {
            return enrichment.categoryId() === category.id();
          });
        }, this));
        this.enrichmentsFilterSubcategory = ko.computed(__bind(function() {
          var subcategory;
          subcategory = this.subcategoryFilter();
          if (subcategory === '') {
            return this.enrichmentsFilterCategory();
          }
          return ko.utils.arrayFilter(this.enrichmentsFilterCategory(), function(enrichment) {
            return enrichment.subcategoryId() === subcategory.id();
          });
        }, this));
        this.newSpecies = {
          commonName: ko.observable(''),
          scientificName: ko.observable('')
        };
        this.newSpeciesError = ko.observable(null);
        this.newSpeciesWarning = ko.observable(null);
        this.newSpeciesSuccess = ko.observable(false);
        this.newSpeciesIsCreating = ko.observable(true);
        this.newSpeciesAjaxLoad = ko.observable(false);
        this.newExhibit = {
          code: ko.observable('')
        };
        this.newExhibitError = ko.observable(null);
        this.newExhibitWarning = ko.observable(null);
        this.newExhibitSuccess = ko.observable(false);
        this.newExhibitIsCreating = ko.observable(true);
        this.newExhibitAjaxLoad = ko.observable(false);
        this.newHousingGroup = {
          name: ko.observable(''),
          exhibit: ko.observable('')
        };
        this.newHousingGroupError = ko.observable(null);
        this.newHousingGroupWarning = ko.observable(null);
        this.newHousingGroupSuccess = ko.observable(false);
        this.newHousingGroupIsCreating = ko.observable(true);
        this.newHousingGroupAjaxLoad = ko.observable(false);
        this.newAnimal = {
          count: ko.observable('1'),
          housingGroup: ko.observable(''),
          name: ko.observable(''),
          species: ko.observable(''),
          exhibit: ko.observable({
            housingGroups: ko.observableArray([])
          })
        };
        this.newAnimalError = ko.observable(null);
        this.newAnimalWarning = ko.observable(null);
        this.newAnimalSuccess = ko.observable(false);
        this.newAnimalIsCreating = ko.observable(true);
        this.newAnimalAjaxLoad = ko.observable(false);
        this.uploadDisableSubmit = ko.observable(true);
        this.uploadEnablePreview = ko.observable(false);
        this.uploadAnimals = [];
        this.uploadAnimalsPreview = ko.observableArray([]);
        this.uploadErrorMessageBody = ko.observable('');
        this.uploadErrorMessageEnable = ko.observable(false);
        this.uploadWarningMessageBody = ko.observable('');
        this.uploadWarningMessageEnable = ko.observable(false);
        this.uploadAjaxInProgress = ko.observable(false);
        this.uploadUploadSuccess = ko.observable(false);
        this.uploadIncludeFirstLine = ko.observable(true);
        self = this;
        document.getElementById('file_upload').onchange = function() {
          var file, reader;
          file = this.files[0];
          console.log(file);
          self.uploadDisableSubmit(true);
          self.uploadEnablePreview(false);
          self.uploadErrorMessageEnable(false);
          self.uploadWarningMessageEnable(false);
          reader = new FileReader();
          console.log(reader);
          reader.onload = function(ev) {
            var field, fields, hasBlankField, i, line, lines, _i, _len, _len2;
            if (ev.target.result === "") {
              self.uploadErrorMessageEnable(true);
              self.uploadErrorMessageBody('The file is empty');
              return;
            }
            lines = ev.target.result.split(/[\n|\r]/);
            self.uploadAnimals = [];
            self.uploadAnimalsPreview([]);
            for (i = 0, _len = lines.length; i < _len; i++) {
              line = lines[i];
              fields = line.split(',');
              console.log(i);
              console.log(fields);
              if (fields.length === 0) {
                console.log("The line is empty");
                continue;
              }
              if (fields.length !== 7) {
                if (!self.uploadWarningMessageEnable()) {
                  self.uploadWarningMessageEnable(true);
                  self.uploadWarningMessageBody("Line " + (i + 1) + ": has " + fields.length + " fields");
                }
                continue;
              }
              if (!parseInt(fields[0])) {
                if (!self.uploadWarningMessageEnable()) {
                  self.uploadWarningMessageEnable(true);
                  self.uploadWarningMessageBody("Line " + (i + 1) + ": ID must be an integer (\"" + fields[0] + "\")");
                }
                continue;
              }
              if (!parseInt(fields[6])) {
                if (!self.uploadWarningMessageEnable()) {
                  self.uploadWarningMessageEnable(true);
                  self.uploadWarningMessageBody("Line " + (i + 1) + ": Count must be an integer (\"" + fields[6] + "\")");
                }
                continue;
              }
              hasBlankField = false;
              for (_i = 0, _len2 = fields.length; _i < _len2; _i++) {
                field = fields[_i];
                if (field === "") {
                  console.log("field is bad!");
                  hasBlankField = true;
                  break;
                }
              }
              if (hasBlankField) {
                if (!self.uploadWarningMessageEnable()) {
                  self.uploadWarningMessageEnable(true);
                  self.uploadWarningMessageBody("Line " + (i + 1) + " has blank fields and has been excluded.");
                }
                continue;
              }
              self.uploadAnimals.push(line);
              self.uploadAnimalsPreview.push({
                id: fields[0],
                speciesCommonName: fields[1],
                speciesScientificName: fields[2],
                exhibit: fields[3],
                houseGroupName: fields[4],
                houseName: fields[5],
                count: fields[6]
              });
            }
            if (self.uploadAnimals.length > 0) {
              self.uploadDisableSubmit(false);
              return self.uploadEnablePreview(true);
            } else {
              self.uploadWarningMessageEnable(false);
              self.uploadErrorMessageEnable(true);
              return self.uploadErrorMessageBody("" + file.name + " is not in the proper format");
            }
          };
          return reader.readAsText(file);
        };
      }
      AnimalListViewModel.prototype.openCreateSpecies = function() {
        this.newSpecies.commonName('');
        this.newSpecies.scientificName('');
        this.newSpeciesError(null);
        this.newSpeciesWarning(null);
        this.newSpeciesSuccess(false);
        this.newSpeciesIsCreating(true);
        return this.newSpeciesAjaxLoad(false);
      };
      AnimalListViewModel.prototype.createNewSpecies = function() {
        var newSpecies, settings;
        newSpecies = {
          common_name: this.newSpecies.commonName(),
          scientific_name: this.newSpecies.scientificName()
        };
        if (newSpecies.common_name.length === 0) {
          this.newSpeciesError('Common Name cannot be empty');
          return;
        }
        if (newSpecies.scientific_name.length === 0) {
          this.newSpeciesError('Scientific Name cannot be empty');
          return;
        }
        if (newSpecies.common_name.length > 100) {
          this.newSpeciesError('Common Name cannot more than 100 characters');
          return;
        }
        if (newSpecies.scientific_name.length > 200) {
          this.newSpeciesError('Scientific Name cannot be more than 200 characters');
          return;
        }
        settings = {
          type: 'POST',
          url: '/api/v1/species/?format=json',
          data: JSON.stringify(newSpecies),
          dataType: "json",
          processData: false,
          contentType: "application/json"
        };
        settings.success = __bind(function(data, textStatus, jqXHR) {
          console.log("New Species created");
          console.log(data);
          console.log(textStatus);
          this.newSpeciesSuccess(("Species " + newSpecies.common_name + " ") + ("(" + newSpecies.scientific_name + ") was created"));
          this.newSpeciesError(null);
          this.newSpeciesAjaxLoad(false);
          return this.species(new Species(data));
        }, this);
        settings.error = __bind(function(jqXHR, textStatus, errorThrown) {
          console.log("Species error");
          this.newSpeciesError('An unexpected error occured');
          return this.newSpeciesAjaxLoad(false);
        }, this);
        this.newSpeciesAjaxLoad(true);
        return $.ajax(settings);
      };
      AnimalListViewModel.prototype.openCreateExhibit = function() {
        this.newExhibit.code('');
        this.newExhibitError(null);
        this.newExhibitWarning(null);
        this.newExhibitSuccess(false);
        this.newExhibitIsCreating(true);
        return this.newExhibitAjaxLoad(false);
      };
      AnimalListViewModel.prototype.createNewExhibit = function() {
        var newExhibit, settings;
        newExhibit = {
          code: this.newExhibit.code()
        };
        if (newExhibit.code.length === 0) {
          this.newExhibitError('Code cannot be empty');
          return;
        }
        if (newExhibit.code.length > 100) {
          this.newExhibitError('Code cannot more than 100 characters');
          return;
        }
        settings = {
          type: 'POST',
          url: '/api/v1/exhibit/?format=json',
          data: JSON.stringify(newExhibit),
          dataType: "json",
          processData: false,
          contentType: "application/json"
        };
        settings.success = __bind(function(data, textStatus, jqXHR) {
          console.log("New Exhibit created");
          console.log(data);
          console.log(textStatus);
          this.newExhibitSuccess("Exhibit " + newExhibit.code + " was created");
          this.newExhibitError(null);
          this.newExhibitAjaxLoad(false);
          return this.exhibits.push(new Exhibit(data));
        }, this);
        settings.error = __bind(function(jqXHR, textStatus, errorThrown) {
          console.log("Create exhibit error");
          this.newExhibitError('An unexpected error occured');
          return this.newExhibitAjaxLoad(false);
        }, this);
        this.newExhibitAjaxLoad(true);
        return $.ajax(settings);
      };
      AnimalListViewModel.prototype.openCreateHousingGroup = function() {
        this.newHousingGroup.name('');
        this.newHousingGroup.exhibit('');
        this.newHousingGroupError(null);
        this.newHousingGroupWarning(null);
        this.newHousingGroupSuccess(false);
        this.newHousingGroupIsCreating(true);
        return this.newHousingGroupAjaxLoad(false);
      };
      AnimalListViewModel.prototype.createNewHousingGroup = function() {
        var newHousingGroup, settings;
        newHousingGroup = {
          name: this.newHousingGroup.name(),
          exhibit: this.newHousingGroup.exhibit().resourceURI
        };
        console.log(newHousingGroup);
        if (newHousingGroup.name.length === 0) {
          this.newHousingGroupError('Name cannot be empty');
          return;
        }
        if (newHousingGroup.name.length > 100) {
          this.newHousingGroupError('Name cannot more than 100 characters');
          return;
        }
        settings = {
          type: 'POST',
          url: '/api/v1/housingGroup/?format=json',
          data: JSON.stringify(newHousingGroup),
          dataType: "json",
          processData: false,
          contentType: "application/json"
        };
        settings.success = __bind(function(data, textStatus, jqXHR) {
          console.log("New HousingGroup created");
          console.log(data);
          console.log(textStatus);
          this.newHousingGroupSuccess(("HousingGroup " + newHousingGroup.name + " ") + ("for exhibit " + (this.newHousingGroup.exhibit().code()) + " was created"));
          this.newHousingGroupError(null);
          this.newHousingGroupAjaxLoad(false);
          return this.newHousingGroup.exhibit().housingGroups.push(new HousingGroup(data));
        }, this);
        settings.error = __bind(function(jqXHR, textStatus, errorThrown) {
          console.log("Create housinggroup error");
          this.newHousingGroupError('An unexpected error occured');
          return this.newHousingGroupAjaxLoad(false);
        }, this);
        this.newHousingGroupAjaxLoad(true);
        return $.ajax(settings);
      };
      AnimalListViewModel.prototype.openCreateAnimal = function() {
        this.newAnimal.count('1');
        this.newAnimal.housingGroup('');
        this.newAnimal.name('');
        this.newAnimal.species('');
        this.newAnimal.exhibit({
          housingGroups: ko.observableArray([])
        });
        this.newAnimalError(null);
        this.newAnimalWarning(null);
        this.newAnimalSuccess(false);
        this.newAnimalIsCreating(true);
        return this.newAnimalAjaxLoad(false);
      };
      AnimalListViewModel.prototype.createNewAnimal = function() {
        var newAnimal, settings;
        newAnimal = {
          count: parseInt(this.newAnimal.count()),
          housing_group: this.newAnimal.housingGroup().resourceURI,
          name: this.newAnimal.name(),
          species: this.newAnimal.species().resourceURI
        };
        if (this.newAnimal.count().length === 0) {
          this.newAnimalError('Count cannot be empty');
          return;
        }
        if (newAnimal.count <= 0) {
          this.newAnimalError('Count must be a positive integer');
          return;
        }
        if (!newAnimal.count) {
          this.newAnimalError('Count must be a number');
          return;
        }
        if (newAnimal.name.length === 0) {
          this.newAnimalError('Name cannot be empty');
          return;
        }
        if (newAnimal.name.length > 100) {
          this.newAnimalError('Name cannot more than 100 characters');
          return;
        }
        settings = {
          type: 'POST',
          url: '/api/v1/animal/?format=json',
          data: JSON.stringify(newAnimal),
          dataType: "json",
          processData: false,
          contentType: "application/json"
        };
        settings.success = __bind(function(data, textStatus, jqXHR) {
          console.log("New Animal created");
          console.log(data);
          console.log(textStatus);
          this.newAnimalSuccess("Animal " + newAnimal.name + " was created");
          this.newAnimalError(null);
          this.newAnimalAjaxLoad(false);
          return this.newAnimal.housingGroup().animals.push(new Animal(data));
        }, this);
        settings.error = __bind(function(jqXHR, textStatus, errorThrown) {
          console.log("Create animal error");
          this.newAnimalError('An unexpected error occured');
          return this.newAnimalAjaxLoad(false);
        }, this);
        this.newAnimalAjaxLoad(true);
        return $.ajax(settings);
      };
      AnimalListViewModel.prototype.openInfo = function() {
        this.staffs([]);
        $.each(this.selectedAnimals(), __bind(function(index, animal) {
          console.log(animal);
          return $.getJSON("/api/v1/staff/?format=json&animal_id=" + (animal.id()), __bind(function(data) {
            return $.each(data.objects, __bind(function(index, item) {
              return this.staffs.push(new Staff(item));
            }, this));
          }, this));
        }, this));
        return $('#modal-animal-info').modal('show');
      };
      AnimalListViewModel.prototype.openBulkUpload = function() {
        $('#file_upload').val('');
        this.uploadDisableSubmit(true);
        this.uploadEnablePreview(false);
        this.uploadAnimals = [];
        this.uploadAnimalsPreview([]);
        this.uploadErrorMessageEnable(false);
        this.uploadWarningMessageEnable(false);
        this.uploadAjaxInProgress(false);
        this.uploadUploadSuccess(false);
        return this.uploadIncludeFirstLine(true);
      };
      AnimalListViewModel.prototype.sendBulkUpload = function() {
        var settings, uploadAnimals;
        uploadAnimals = this.uploadAnimals;
        if (!this.uploadIncludeFirstLine()) {
          uploadAnimals = uploadAnimals.slice(1, uploadAnimals.length);
        }
        settings = {
          type: 'POST',
          url: '/api/v1/animal/bulk/?format=json',
          data: JSON.stringify(uploadAnimals),
          dataType: "json",
          processData: false,
          contentType: "application/json"
        };
        settings.success = __bind(function(data, textStatus, jqXHR) {
          console.log("Batch animals created");
          console.log(data);
          console.log(textStatus);
          this.uploadUploadSuccess(true);
          this.uploadErrorMessageEnable(false);
          this.uploadWarningMessageEnable(false);
          return this.load();
        }, this);
        settings.error = __bind(function(jqXHR, textStatus, errorThrown) {
          console.log("Batch animals error");
          this.uploadErrorMessageEnable(true);
          this.uploadWarningMessageEnable(false);
          this.uploadErrorMessageBody('An unexpected error occured');
          return this.uploadAjaxInProgress(false);
        }, this);
        this.uploadAjaxInProgress(true);
        return $.ajax(settings);
      };
      AnimalListViewModel.prototype.toggleViewAll = function() {
        return this.viewAll(!this.viewAll());
      };
      AnimalListViewModel.prototype.filterCategory = function(category) {
        if (category === this.categoryFilter()) {
          this.subcategoryFilter('');
          this.categoryFilter('');
        } else {
          this.subcategoryFilter('');
          this.categoryFilter(category);
        }
        return resizeAllCarousels();
      };
      AnimalListViewModel.prototype.filterSubcategory = function(subcategory) {
        if (subcategory === this.subcategoryFilter()) {
          this.subcategoryFilter('');
        } else {
          this.subcategoryFilter(subcategory);
        }
        return resizeAllCarousels();
      };
      AnimalListViewModel.prototype.setCurrentSpecies = function(species) {
        if (species === this.currentSpecies()) {
          this.currentSpecies('');
        } else {
          this.currentSpecies(species);
        }
        return resizeAllCarousels();
      };
      AnimalListViewModel.prototype.isSelected = function(animal) {
        return animal.active();
      };
      AnimalListViewModel.prototype.selectAnimal = function(animal) {
        this.selectedAnimalsChanged = true;
        animal.active(true);
        return this.selectedAnimals.push(animal);
      };
      AnimalListViewModel.prototype.deselectAnimal = function(animal) {
        animal.active(false);
        return this.selectedAnimals.remove(animal);
      };
      AnimalListViewModel.prototype.toggleAnimal = function(animal) {
        if (!this.isSelected(animal)) {
          return this.selectAnimal(animal);
        } else {
          return this.deselectAnimal(animal);
        }
      };
      AnimalListViewModel.prototype.selectExhibit = function(exhibit) {
        var deselectAnimals, selectAnimals;
        selectAnimals = [];
        deselectAnimals = [];
        $.each(exhibit.housingGroups(), __bind(function(i, hg) {
          return $.each(hg.animals(), __bind(function(index, animal) {
            if (!this.isSelected(animal)) {
              return selectAnimals.push(animal);
            } else {
              return deselectAnimals.push(animal);
            }
          }, this));
        }, this));
        if (selectAnimals.length > 0) {
          return $.each(selectAnimals, __bind(function(index, animal) {
            return this.selectAnimal(animal);
          }, this));
        } else {
          return $.each(deselectAnimals, __bind(function(index, animal) {
            return this.deselectAnimal(animal);
          }, this));
        }
      };
      AnimalListViewModel.prototype.selectHousingGroup = function(housingGroup) {
        var deselectAnimals, selectAnimals;
        selectAnimals = [];
        deselectAnimals = [];
        $.each(housingGroup.animals(), __bind(function(index, animal) {
          if (!this.isSelected(animal)) {
            return selectAnimals.push(animal);
          } else {
            return deselectAnimals.push(animal);
          }
        }, this));
        if (selectAnimals.length > 0) {
          return $.each(selectAnimals, __bind(function(index, animal) {
            return this.selectAnimal(animal);
          }, this));
        } else {
          return $.each(deselectAnimals, __bind(function(index, animal) {
            return this.deselectAnimal(animal);
          }, this));
        }
      };
      AnimalListViewModel.prototype.newObservation = function() {
        if (this.selectedAnimalsChanged) {
          $.each(this.selectedAnimals(), __bind(function(index, animal) {
            if (this.selectedAnimals()[index].observation() === null) {
              return this.selectedAnimals()[index].observation(new AnimalObservation());
            }
          }, this));
          this.loadEnrichments();
        }
        return this.selectedAnimalsChanged = false;
      };
      AnimalListViewModel.prototype.selectEnrichment = function(enrichment) {
        return this.currentEnrichment(enrichment);
      };
      AnimalListViewModel.prototype.load = function() {
        $.getJSON('/api/v1/exhibit/?format=json&limit=0', __bind(function(data) {
          var mappedExhibits;
          mappedExhibits = $.map(data.objects, function(item) {
            return new Exhibit(item);
          });
          return this.exhibits(mappedExhibits);
        }, this));
        return $.getJSON('/api/v1/species/?format=json&limit=0', __bind(function(data) {
          var mappedSpecies;
          mappedSpecies = $.map(data.objects, function(item) {
            return new Species(item);
          });
          return this.species(ko.toJS(mappedSpecies));
        }, this));
      };
      AnimalListViewModel.prototype.idInArray = function(id, array) {
        var retval;
        retval = false;
        $.each(array, __bind(function(index, value) {
          if (id === value.id()) {
            retval = true;
            return false;
          }
        }, this));
        return retval;
      };
      AnimalListViewModel.prototype.loadEnrichments = function() {
        var speciesSet, url;
        speciesSet = {};
        $.each(this.selectedAnimals(), __bind(function(index, animal) {
          return speciesSet[animal.speciesId()] = true;
        }, this));
        url = '/api/v1/enrichmentNote/?format=json&limit=0&species_id=';
        $.each(speciesSet, __bind(function(key, value) {
          return url += key + ',';
        }, this));
        this.enrichmentNotes([]);
        this.enrichments([]);
        this.subcategories([]);
        this.categories([]);
        this.currentEnrichment(null);
        return $.getJSON(url, __bind(function(data) {
          var mappedEnrichmentNotes;
          mappedEnrichmentNotes = $.map(data.objects, __bind(function(item) {
            var enrichmentNote, tempCategory, tempEnrichment, tempSubcategory;
            enrichmentNote = new EnrichmentNote(item);
            tempEnrichment = new Enrichment(item.enrichment);
            if (!this.idInArray(tempEnrichment.id(), this.enrichments())) {
              this.enrichments.push(tempEnrichment);
            }
            tempSubcategory = new Subcategory(item.enrichment.subcategory);
            if (!this.idInArray(tempSubcategory.id(), this.subcategories())) {
              this.subcategories.push(tempSubcategory);
            }
            tempCategory = new Category(item.enrichment.subcategory.category);
            if (!this.idInArray(tempCategory.id(), this.categories())) {
              this.categories.push(tempCategory);
            }
            return enrichmentNote;
          }, this));
          this.enrichmentNotes(mappedEnrichmentNotes);
          this.enrichments.sort(function(a, b) {
            if (a.name() === b.name()) {
              return 0;
            } else if (a.name() < b.name()) {
              return -1;
            } else {
              return 1;
            }
          });
          return resizeAllCarousels();
        }, this));
      };
      AnimalListViewModel.prototype.createObservation = function() {
        var newObservation, settings;
        newObservation = {
          enrichment: '/api/v1/enrichment/' + this.currentEnrichment().id() + '/',
          staff: '/api/v1/staff/' + window.userId + '/',
          date_created: new Date().toISOString().split('.')[0]
        };
        if (this.newObservationAjaxLoad()) {
          console.log("We are already trying to send something");
          return false;
        }
        settings = {
          type: 'POST',
          url: '/api/v1/observation/?format=json',
          data: JSON.stringify(newObservation),
          dataType: "json",
          processData: false,
          contentType: "application/json"
        };
        settings.success = __bind(function(data, textStatus, jqXHR) {
          var locationsURL, pieces;
          console.log("Observation successfully created!");
          console.log(jqXHR.getResponseHeader('Location'));
          locationsURL = jqXHR.getResponseHeader('Location');
          pieces = locationsURL.split("/");
          newObservation.id = pieces[pieces.length - 2];
          this.newObservationIsCreating(false);
          this.newObservationSuccess(true);
          this.newObservationError(null);
          console.log(newObservation);
          this.createAnimalObservation(newObservation.id);
          this.newObservationAjaxLoad(false);
          $.each(this.selectedAnimals(), __bind(function(index, animal) {
            return animal.active(false);
          }, this));
          this.currentEnrichment(null);
          return $('#modal-observe-1').modal('hide').on('hidden', function() {
            return sammy.setLocation('/observe');
          });
        }, this);
        settings.error = __bind(function(jqXHR, textStatus, errorThrown) {
          console.log("Observation not created!");
          this.newObservationNameErrorMessage(true);
          this.newObservationAjaxLoad(false);
          return this.newObservationNameMessageBody('An unexpected error occured');
        }, this);
        this.newObservationAjaxLoad(true);
        return $.ajax(settings);
      };
      AnimalListViewModel.prototype.createAnimalObservation = function(observationId) {
        var animal, newAnimalObservation, settings, _i, _len, _ref, _results;
        _ref = this.selectedAnimals();
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          animal = _ref[_i];
          newAnimalObservation = {
            animal: '/api/v1/animal/' + animal.id() + '/',
            observation: '/api/v1/observation/' + observationId + '/'
          };
          settings = {
            type: 'POST',
            url: '/api/v1/animalObservation/?format=json',
            data: JSON.stringify(newAnimalObservation),
            dataType: "json",
            processData: false,
            contentType: "application/json"
          };
          settings.success = __bind(function(data, textStatus, jqXHR) {
            var locationsURL, pieces;
            console.log("Animalobservation successfully created!");
            locationsURL = jqXHR.getResponseHeader('Location');
            pieces = locationsURL.split("/");
            newAnimalObservation.id = pieces[pieces.length - 2];
            this.newAnimalObservationIsCreating(false);
            this.newAnimalObservationSuccess(true);
            this.newAnimalObservationError(null);
            return console.log(newAnimalObservation);
          }, this);
          settings.error = __bind(function(jqXHR, textStatus, errorThrown) {
            console.log("Animalobservation not created!");
            this.newAnimalObservationNameErrorMessage(true);
            return this.newAnimalObservationNameMessageBody('An unexpected error occured');
          }, this);
          _results.push($.ajax(settings));
        }
        return _results;
      };
      AnimalListViewModel.prototype.empty = function() {
        this.animals([]);
        this.exhibits([]);
        this.categories([]);
        this.subcategories([]);
        this.enrichments([]);
        this.enrichmentNotes([]);
        return this.currentSpecies('');
      };
      return AnimalListViewModel;
    })();
    EnrichmentListViewModel = (function() {
      function EnrichmentListViewModel() {
        this.createEnrichmentNote = __bind(this.createEnrichmentNote, this);
        this.createEnrichment = __bind(this.createEnrichment, this);
        this.createSubcategory = __bind(this.createSubcategory, this);
        this.createCategory = __bind(this.createCategory, this);
        this.openEnrichmentNote = __bind(this.openEnrichmentNote, this);
        this.openCreateEnrichment = __bind(this.openCreateEnrichment, this);
        this.openCreateSubcategory = __bind(this.openCreateSubcategory, this);
        this.openCreateCategory = __bind(this.openCreateCategory, this);
        this.empty = __bind(this.empty, this);
        this.load = __bind(this.load, this);
        this.filterSubcategory = __bind(this.filterSubcategory, this);
        this.filterCategory = __bind(this.filterCategory, this);        this.categories = ko.observableArray([]);
        this.subcategories = ko.observableArray([]);
        this.enrichments = ko.observableArray([]);
        this.species = ko.observableArray([]);
        this.categoryFilter = ko.observable('');
        this.subcategoryFilter = ko.observable('');
        this.subcategoriesFilterCategory = ko.computed(__bind(function() {
          var category;
          category = this.categoryFilter();
          if (category === '') {
            return [];
          }
          return ko.utils.arrayFilter(this.subcategories(), function(subcategory) {
            return subcategory.categoryId() === category.id();
          });
        }, this));
        this.enrichmentsFilterCategory = ko.computed(__bind(function() {
          var category;
          category = this.categoryFilter();
          if (category === '') {
            return this.enrichments();
          }
          return ko.utils.arrayFilter(this.enrichments(), function(enrichment) {
            return enrichment.categoryId() === category.id();
          });
        }, this));
        this.enrichmentsFilterSubcategory = ko.computed(__bind(function() {
          var subcategory;
          subcategory = this.subcategoryFilter();
          if (subcategory === '') {
            return this.enrichmentsFilterCategory();
          }
          return ko.utils.arrayFilter(this.enrichmentsFilterCategory(), function(enrichment) {
            return enrichment.subcategoryId() === subcategory.id();
          });
        }, this));
        this.newCategory = {
          name: ko.observable('')
        };
        this.newCategoryNameErrorMessage = ko.observable(false);
        this.newCategoryNameSuccessMessage = ko.observable(false);
        this.newCategoryNameMessageBody = ko.observable('');
        this.newCategoryAjaxLoad = ko.observable(false);
        this.newCategoryIsCreating = ko.observable(true);
        this.newSubcategoryOptions = ko.computed(__bind(function() {
          return ko.utils.arrayFilter(this.subcategories(), __bind(function(subcategory) {
            return subcategory.categoryId() === this.newEnrichment.category().id();
          }, this));
        }, this));
        this.newSubcategory = {
          name: ko.observable(''),
          category: ko.observable('')
        };
        this.newSubcategoryNameErrorMessage = ko.observable(false);
        this.newSubcategoryNameSuccessMessage = ko.observable(false);
        this.newSubcategoryNameMessageBody = ko.observable('');
        this.newSubcategoryAjaxLoad = ko.observable(false);
        this.newSubcategoryIsCreating = ko.observable(true);
        this.newEnrichment = {
          name: ko.observable(''),
          category: ko.observable(''),
          subcategory: ko.observable('')
        };
        this.newEnrichmentNameErrorMessage = ko.observable(false);
        this.newEnrichmentNameSuccessMessage = ko.observable(false);
        this.newEnrichmentNameMessageBody = ko.observable('');
        this.newEnrichmentAjaxLoad = ko.observable(false);
        this.newEnrichmentIsCreating = ko.observable(true);
        this.newEnrichmentNote = new EnrichmentNote(null);
        this.newEnrichmentNoteError = ko.observable(false);
        this.newEnrichmentNoteSuccess = ko.observable(false);
        this.newEnrichmentNoteAjaxLoad = ko.observable(false);
        this.newEnrichmentNoteIsCreating = ko.observable(true);
        this.currentEnrichment = ko.observable(new Enrichment(null));
        this.enrichmentNotes = ko.observableArray([]);
      }
      EnrichmentListViewModel.prototype.filterCategory = function(category) {
        if (category === this.categoryFilter()) {
          this.subcategoryFilter('');
          this.categoryFilter('');
        } else {
          this.subcategoryFilter('');
          this.categoryFilter(category);
        }
        return resizeAllCarousels();
      };
      EnrichmentListViewModel.prototype.filterSubcategory = function(subcategory) {
        if (subcategory === this.subcategoryFilter()) {
          this.subcategoryFilter('');
        } else {
          this.subcategoryFilter(subcategory);
        }
        return resizeAllCarousels();
      };
      EnrichmentListViewModel.prototype.load = function() {
        $.getJSON('/api/v1/category/?format=json', __bind(function(data) {
          var mappedCategories;
          mappedCategories = $.map(data.objects, function(item) {
            return new Category(item);
          });
          return this.categories(mappedCategories);
        }, this));
        $.getJSON('/api/v1/subcategory/?format=json', __bind(function(data) {
          var mappedSubcategories;
          mappedSubcategories = $.map(data.objects, function(item) {
            return new Subcategory(item);
          });
          return this.subcategories(mappedSubcategories);
        }, this));
        $.getJSON('/api/v1/enrichment/?format=json&limit=0', __bind(function(data) {
          var mappedEnrichments;
          mappedEnrichments = $.map(data.objects, function(item) {
            return new Enrichment(item);
          });
          this.enrichments(mappedEnrichments);
          this.enrichments.sort(function(a, b) {
            if (a.name() === b.name()) {
              return 0;
            } else if (a.name() < b.name()) {
              return -1;
            } else {
              return 1;
            }
          });
          return resizeAllCarousels();
        }, this));
        return $.getJSON('/api/v1/species/?format=json&limit=0', __bind(function(data) {
          var mappedSpecies;
          mappedSpecies = $.map(data.objects, function(item) {
            return new Species(item);
          });
          return this.species(mappedSpecies);
        }, this));
      };
      EnrichmentListViewModel.prototype.empty = function() {
        this.categories(null);
        this.subcategories(null);
        this.enrichments(null);
        this.categoryFilter('');
        return this.subcategoryFilter('');
      };
      EnrichmentListViewModel.prototype.openCreateCategory = function() {
        this.newCategory.name('');
        this.newCategoryNameErrorMessage(false);
        this.newCategoryNameSuccessMessage(false);
        this.newCategoryNameMessageBody('');
        this.newCategoryAjaxLoad(false);
        return this.newCategoryIsCreating(true);
      };
      EnrichmentListViewModel.prototype.openCreateSubcategory = function() {
        this.newSubcategory.name('');
        this.newSubcategory.category('');
        this.newSubcategoryNameErrorMessage(false);
        this.newSubcategoryNameSuccessMessage(false);
        this.newSubcategoryNameMessageBody('');
        this.newSubcategoryAjaxLoad(false);
        return this.newSubcategoryIsCreating(true);
      };
      EnrichmentListViewModel.prototype.openCreateEnrichment = function() {
        this.newEnrichment.name('');
        this.newEnrichment.subcategory('');
        this.newEnrichmentNameErrorMessage(false);
        this.newEnrichmentNameSuccessMessage(false);
        this.newEnrichmentNameMessageBody('');
        this.newEnrichmentAjaxLoad(false);
        return this.newEnrichmentIsCreating(true);
      };
      EnrichmentListViewModel.prototype.openEnrichmentNote = function(current) {
        this.newEnrichmentNoteError(false);
        this.newEnrichmentNoteSuccess(false);
        this.newEnrichmentNoteAjaxLoad(false);
        this.newEnrichmentNoteIsCreating(true);
        this.currentEnrichment(current);
        console.log(current.id());
        $.getJSON("/api/v1/enrichmentNote/?format=json&enrichment_id=" + (current.id()), __bind(function(data) {
          var mappedNotes;
          mappedNotes = $.map(data.objects, function(item) {
            return new EnrichmentNote(item);
          });
          return this.enrichmentNotes(mappedNotes);
        }, this));
        $('#modal-enrichment-info').modal('show');
        return console.log(this.currentEnrichment());
      };
      EnrichmentListViewModel.prototype.createCategory = function() {
        var newCategory, settings;
        newCategory = {
          name: this.newCategory.name()
        };
        if (this.newCategoryAjaxLoad()) {
          console.log("We are already trying to send something");
          return false;
        }
        if (newCategory.name.length === 0) {
          this.newCategoryNameErrorMessage(true);
          this.newCategoryNameMessageBody('Category name cannot be blank');
          return;
        }
        if (newCategory.name.length > 100) {
          this.newCategoryNameErrorMessage(true);
          this.newCategoryNameMessageBody('Category name is too long');
          return;
        }
        settings = {
          type: 'POST',
          url: '/api/v1/category/?format=json',
          data: JSON.stringify(newCategory),
          dataType: "json",
          processData: false,
          contentType: "application/json"
        };
        settings.success = __bind(function(data, textStatus, jqXHR) {
          var locationsURL, pieces;
          console.log("Category successfully created!");
          locationsURL = jqXHR.getResponseHeader('Location');
          pieces = locationsURL.split("/");
          newCategory.id = pieces[pieces.length - 2];
          this.newCategoryIsCreating(false);
          this.newCategoryNameSuccessMessage(true);
          this.newCategoryNameErrorMessage(false);
          console.log(newCategory);
          this.categories.push({
            name: ko.observable(newCategory.name),
            id: ko.observable(newCategory.id)
          });
          return resizeAllCarousels();
        }, this);
        settings.error = __bind(function(jqXHR, textStatus, errorThrown) {
          console.log("Category not created!");
          this.newCategoryNameErrorMessage(true);
          this.newCategoryAjaxLoad(false);
          return this.newCategoryNameMessageBody('An unexpected error occured');
        }, this);
        this.newCategoryAjaxLoad(true);
        return $.ajax(settings);
      };
      EnrichmentListViewModel.prototype.createSubcategory = function() {
        var category, newSubcategory, settings;
        category = this.newSubcategory.category();
        newSubcategory = {
          name: this.newSubcategory.name(),
          category: "/api/v1/category/" + (category.id()) + "/"
        };
        console.log(newSubcategory);
        if (this.newSubcategoryAjaxLoad()) {
          console.log("We are already trying to send something");
          return;
        }
        if (newSubcategory.name.length === 0) {
          this.newSubcategoryNameErrorMessage(true);
          this.newSubcategoryNameMessageBody('Subcategory name cannot be blank');
          return;
        }
        if (newSubcategory.name.length > 100) {
          this.newSubcategoryNameErrorMessage(true);
          this.newSubcategoryNameMessageBody('Subcategory name is too long');
          return;
        }
        settings = {
          type: 'POST',
          url: '/api/v1/subcategory/?format=json',
          data: JSON.stringify(newSubcategory),
          success: this.subcategoryCreated,
          dataType: "json",
          processData: false,
          contentType: "application/json"
        };
        settings.success = __bind(function(data, textStatus, jqXHR) {
          var locationsURL, pieces;
          console.log("Subcategory successfully created!");
          locationsURL = jqXHR.getResponseHeader('Location');
          pieces = locationsURL.split("/");
          newSubcategory.id = pieces[pieces.length - 2];
          this.newSubcategoryIsCreating(false);
          this.newSubcategoryNameSuccessMessage(true);
          this.newSubcategoryNameErrorMessage(false);
          this.subcategories.push({
            name: ko.observable(newSubcategory.name),
            id: ko.observable(newSubcategory.id),
            categoryId: ko.observable(category.id())
          });
          return resizeAllCarousels();
        }, this);
        settings.error = __bind(function(jqXHR, textStatus, errorThrown) {
          console.log("Subcategory not created!");
          this.newSubcategoryNameErrorMessage(true);
          this.newSubcategoryAjaxLoad(false);
          return this.newSubcategoryNameMessageBody('An unexpected error occured');
        }, this);
        this.newSubcategoryAjaxLoad(true);
        return $.ajax(settings);
      };
      EnrichmentListViewModel.prototype.createEnrichment = function() {
        var category, newEnrichment, settings, subcategory;
        category = this.newEnrichment.category();
        subcategory = this.newEnrichment.subcategory();
        newEnrichment = {
          name: this.newEnrichment.name(),
          subcategory: "/api/v1/category/" + (subcategory.id()) + "/"
        };
        console.log(newEnrichment);
        if (this.newEnrichmentAjaxLoad()) {
          console.log("We are already trying to send something");
          return;
        }
        if (newEnrichment.name.length === 0) {
          this.newEnrichmentNameErrorMessage(true);
          this.newEnrichmentNameMessageBody('Enrichment name cannot be blank');
          return;
        }
        if (newEnrichment.name.length > 100) {
          this.newEnrichmentNameErrorMessage(true);
          this.newEnrichmentNameMessageBody('Enrichment name is too long');
          return;
        }
        settings = {
          type: 'POST',
          url: '/api/v1/enrichment/?format=json',
          data: JSON.stringify(newEnrichment),
          success: this.enrichmentCreated,
          dataType: "json",
          processData: false,
          contentType: "application/json"
        };
        settings.success = __bind(function(data, textStatus, jqXHR) {
          var locationsURL, pieces;
          console.log("Enrichment successfully created!");
          locationsURL = jqXHR.getResponseHeader('Location');
          pieces = locationsURL.split("/");
          newEnrichment.id = pieces[pieces.length - 2];
          this.newEnrichmentIsCreating(false);
          this.newEnrichmentNameSuccessMessage(true);
          this.newEnrichmentNameErrorMessage(false);
          newEnrichment.subcategory.category = newEnrichment.category;
          this.enrichments.push(new Enrichment(newEnrichment));
          return resizeAllCarousels();
        }, this);
        settings.error = __bind(function(jqXHR, textStatus, errorThrown) {
          console.log("Enrichment not created!");
          this.newEnrichmentNameErrorMessage(true);
          this.newEnrichmentAjaxLoad(false);
          return this.newEnrichmentNameMessageBody('An unexpected error occured');
        }, this);
        this.newEnrichmentAjaxLoad(true);
        return $.ajax(settings);
      };
      EnrichmentListViewModel.prototype.createEnrichmentNote = function() {
        var newEN, settings;
        newEN = {
          enrichment: "/api/v1/enrichment/" + (this.currentEnrichment().id()) + "/",
          instructions: this.newEnrichmentNote.instructions(),
          limitations: this.newEnrichmentNote.limitations(),
          species: "/api/v1/species/" + (this.newEnrichmentNote.species().id()) + "/"
        };
        console.log(newEN);
        if (this.newEnrichmentNoteAjaxLoad()) {
          console.log("We are already trying to send something");
          return;
        }
        settings = {
          type: 'POST',
          url: '/api/v1/enrichmentNote/?format=json',
          data: JSON.stringify(newEN),
          dataType: "json",
          processData: false,
          contentType: "application/json"
        };
        settings.success = __bind(function(data, textStatus, jqXHR) {
          var locationsURL, noteToPush, pieces;
          console.log("EnrichmentNote successfully created!");
          locationsURL = jqXHR.getResponseHeader('Location');
          pieces = locationsURL.split("/");
          noteToPush = {
            enrichment: {
              id: this.currentEnrichment().id()
            },
            instructions: this.newEnrichmentNote.instructions(),
            limitations: this.newEnrichmentNote.limitations(),
            species: {
              common_name: this.newEnrichmentNote.species().commonName()
            },
            id: pieces[pieces.length - 2]
          };
          console.log(noteToPush);
          this.enrichmentNotes.push(new EnrichmentNote(noteToPush));
          this.newEnrichmentNoteSuccess(true);
          this.newEnrichmentNoteError(false);
          this.newEnrichmentNote.instructions(null);
          this.newEnrichmentNote.limitations(null);
          this.newEnrichmentNote.species(null);
          return this.newEnrichmentNoteAjaxLoad(false);
        }, this);
        settings.error = __bind(function(jqXHR, textStatus, errorThrown) {
          console.log("Enrichment not created!");
          this.newEnrichmentAjaxLoad(false);
          return this.newEnrichmentNoteError('An unexpected error occured');
        }, this);
        this.newEnrichmentNoteAjaxLoad(true);
        return $.ajax(settings);
      };
      return EnrichmentListViewModel;
    })();
    ObservationListViewModel = (function() {
      function ObservationListViewModel() {
        this.prettyDate = __bind(this.prettyDate, this);
        this.empty = __bind(this.empty, this);
        this.saveAnimalObservation = __bind(this.saveAnimalObservation, this);
        this.load = __bind(this.load, this);
        this.finishObservation = __bind(this.finishObservation, this);
        this.saveBehavior = __bind(this.saveBehavior, this);
        this.addNewBehavior = __bind(this.addNewBehavior, this);
        this.loadBehaviors = __bind(this.loadBehaviors, this);        this.observations = ko.observableArray([]);
        this.behaviorType = [
          {
            id: 0,
            type: 'N/A'
          }, {
            id: 1,
            type: 'Positive'
          }, {
            id: -1,
            type: 'Negative'
          }, {
            id: -2,
            type: 'Avoid'
          }
        ];
        this.activeObservation = ko.observable(null);
        this.activeAnimalObservation = ko.observable(null);
        this.activeBehaviors = ko.observableArray([]);
        this.newBehaviorType = ko.observable(null);
        this.newBehaviorDesc = ko.observable(null);
        this.selectedBehavior = ko.observable(null);
        updateAnimalObservation.subscribe(__bind(function(data) {
          console.log("saving animal observation");
          return this.saveAnimalObservation(data);
        }, this), this, "saveAnimalObservation");
      }
      ObservationListViewModel.prototype.loadBehaviors = function(observation, animalObservation) {
        this.activeObservation(observation);
        this.activeAnimalObservation(animalObservation);
        console.log("getting behaviors for " + (observation.enrichment().id));
        return $.getJSON("/api/v1/behavior/?format=json&enrichment_id=" + (observation.enrichment().id), __bind(function(data) {
          console.log(data);
          this.activeBehaviors(data.objects);
          return console.log(this.activeBehaviors());
        }, this));
      };
      ObservationListViewModel.prototype.addNewBehavior = function(data) {
        var behavior;
        behavior = {};
        behavior.description = this.newBehaviorDesc();
        behavior.reaction = this.newBehaviorType();
        behavior.enrichment = this.activeObservation().enrichment().resource_uri;
        console.log(behavior);
        return $.ajax("/api/v1/behavior/?format=json", {
          data: JSON.stringify(behavior),
          dataType: "json",
          type: "POST",
          contentType: "application/json",
          processData: false,
          success: __bind(function(result) {
            console.log(result);
            console.log("Created behavior");
            this.activeBehaviors.push(result);
            this.newBehaviorType(null);
            return this.newBehaviorDesc(null);
          }, this),
          error: __bind(function(result) {
            return console.log(result);
          }, this)
        });
      };
      ObservationListViewModel.prototype.saveBehavior = function() {
        var obs;
        try {
          console.log("saving behavior " + (this.selectedBehavior().id) + " for " + (this.activeAnimalObservation().id));
        } catch (TypeError) {
          return;
        }
        console.log(this.selectedBehavior());
        obs = {};
        obs.behavior = this.selectedBehavior().resource_uri;
        console.log(obs);
        return $.ajax("/api/v1/animalObservation/" + (this.activeAnimalObservation().id) + "/?format=json", {
          data: JSON.stringify(obs),
          dataType: "json",
          type: "PATCH",
          contentType: "application/json",
          processData: false,
          success: __bind(function(result) {
            console.log("finished saving behavior");
            console.log(result);
            this.activeObservation(null);
            this.activeBehaviors([]);
            this.activeAnimalObservation(null);
            return this.selectedBehavior(null);
          }, this),
          error: __bind(function(result) {
            return console.log(result);
          }, this)
        });
      };
      ObservationListViewModel.prototype.finishObservation = function() {
        var obs;
        try {
          console.log("finishing observation: " + this.activeObservation().id);
        } catch (TypeError) {
          return;
        }
        obs = {};
        obs.date_finished = new Date().toISOString().split('.')[0];
        console.log(obs);
        return $.ajax("/api/v1/observation/" + (this.activeObservation().id) + "/?format=json", {
          data: JSON.stringify(obs),
          dataType: "json",
          type: "PATCH",
          contentType: "application/json",
          processData: false,
          success: __bind(function(result) {
            console.log("finished observation");
            this.observations.remove(this.activeObservation());
            return this.activeObservation(null);
          }, this),
          error: __bind(function(result) {
            return console.log(result);
          }, this)
        });
      };
      ObservationListViewModel.prototype.load = function() {
        return $.getJSON('/api/v1/observation/?format=json&staff_id=' + window.userId, __bind(function(data) {
          var mapped;
          mapped = $.map(data.objects, function(item) {
            return new Observation(item);
          });
          this.observations(mapped);
          return this.observations.subscribe(function(value) {
            console.log(value);
            return console.log("observation change");
          });
        }, this));
      };
      ObservationListViewModel.prototype.saveAnimalObservation = function(data) {
        var obs;
        console.log("here");
        obs = {};
        obs[data.type] = data.value;
        console.log(JSON.stringify(obs));
        $.ajax("/api/v1/animalObservation/" + data.id + "/?format=json", {
          data: JSON.stringify(obs),
          dataType: "json",
          type: "PATCH",
          contentType: "application/json",
          processData: false,
          success: __bind(function(result) {
            return console.log(result);
          }, this),
          error: __bind(function(result) {
            return console.log(result);
          }, this)
        });
      };
      ObservationListViewModel.prototype.empty = function() {
        return this.observations([]);
      };
      ObservationListViewModel.prototype.prettyDate = function(date) {
        var d;
        d = new Date(Date.parse(date));
        return d.toString();
      };
      return ObservationListViewModel;
    })();
    StaffListViewModel = (function() {
      function StaffListViewModel() {
        this.viewInfo = __bind(this.viewInfo, this);
        this.deleteHousingGroup = __bind(this.deleteHousingGroup, this);
        this.addHousingGroup = __bind(this.addHousingGroup, this);
        this.bulkCreateStaff = __bind(this.bulkCreateStaff, this);
        this.fileChanged = __bind(this.fileChanged, this);
        this.openStaffCreate = __bind(this.openStaffCreate, this);        this.staff = ko.observableArray([]);
        this.currentStaff = ko.observable({
          full_name: '',
          animal_title: '',
          housingGroups: [],
          loading: false,
          id: ''
        });
        this.exhibits = ko.observable(null);
        this.housingGroups = ko.observable(null);
        this.newStaff = {
          firstName: ko.observable(''),
          lastName: ko.observable(''),
          password1: ko.observable(''),
          password2: ko.observable(''),
          isSuperuser: ko.observable(false)
        };
        this.newStaffError = ko.observable(null);
        this.newStaffWarning = ko.observable(null);
        this.newStaffSuccess = ko.observable(false);
        this.newStaffIsCreating = ko.observable(true);
        this.newStaffAjaxLoad = ko.observable(false);
        this.bulkStaff = ko.observableArray([]);
        this.bulkError = ko.observable(null);
        this.bulkWarning = ko.observable(null);
        this.bulkSuccess = ko.observable(null);
        this.bulkAjaxInProgress = ko.observable(false);
        this.newHousingGroup = {
          exhibit: ko.observable(null),
          housingGroup: ko.observable(null)
        };
        this.newHousingGroupError = ko.observable(null);
        this.newHousingGroupWarning = ko.observable(null);
        this.newHousingGroupSuccess = ko.observable(false);
        this.newHousingGroupIsCreating = ko.observable(true);
        this.newHousingGroupAjaxLoad = ko.observable(false);
        this.newHousingGroupOptions = ko.computed(__bind(function() {
          if (this.newHousingGroup.exhibit() != null) {
            return this.newHousingGroup.exhibit().housingGroups();
          } else {
            return [];
          }
        }, this));
        this.newHousingGroupAnimals = ko.computed(__bind(function() {
          if (this.newHousingGroup.housingGroup() != null) {
            return this.newHousingGroup.housingGroup().animals();
          } else {
            return [];
          }
        }, this));
      }
      StaffListViewModel.prototype.openStaffCreate = function() {
        this.newStaff.firstName('');
        this.newStaff.lastName('');
        this.newStaff.password1('');
        this.newStaff.password2('');
        this.newStaff.isSuperuser(false);
        this.newStaffError(null);
        this.newStaffWarning(null);
        this.newStaffSuccess(false);
        this.newStaffIsCreating(true);
        this.newStaffAjaxLoad(false);
        return console.log('openStaffCreate');
      };
      StaffListViewModel.prototype.openBulkCreate = function() {
        $('input[type="file"]').val('');
        this.bulkStaff([]);
        this.bulkError(null);
        this.bulkWarning(null);
        this.bulkSuccess(null);
        return this.bulkAjaxInProgress(false);
      };
      StaffListViewModel.prototype.fileChanged = function(viewModel, event) {
        var file, reader;
        file = event.target.files[0];
        reader = new FileReader();
        this.bulkStaff([]);
        this.bulkWarning(null);
        this.bulkError(null);
        reader.onload = __bind(function(ev) {
          var anyLinesIncluded, fields, index, line, lines, staffObj, tempIndex, _len;
          lines = ev.target.result.split(/[\n|\r]/);
          console.log(lines);
          anyLinesIncluded = false;
          for (index = 0, _len = lines.length; index < _len; index++) {
            line = lines[index];
            tempIndex = index + 1;
            staffObj = {
              line: line,
              lineNumber: ko.observable(tempIndex),
              firstName: ko.observable(''),
              lastName: ko.observable(''),
              password: ko.observable(''),
              isSuperuser: ko.observable('No'),
              validLine: ko.observable(false),
              includeLine: ko.observable(false)
            };
            this.bulkStaff.push(staffObj);
            fields = line.split(',');
            if (line === "") {
              if (index !== lines.length) {
                this.bulkWarning("Line " + tempIndex + ": Line is empty");
              }
              continue;
            }
            if (fields.length !== 4) {
              this.bulkWarning("Line " + tempIndex + ": Invalid amount of lines");
              continue;
            }
            if (fields[0] === "") {
              this.bulkWarning("Line " + tempIndex + ": First name is empty");
              continue;
            }
            if (fields[1] === "") {
              this.bulkWarning("Line " + tempIndex + ": Last name is empty");
              continue;
            }
            if (fields[2] === "") {
              this.bulkWarning("Line " + tempIndex + ": Password is empty");
              continue;
            }
            staffObj.firstName(fields[0]);
            staffObj.lastName(fields[1]);
            staffObj.password(fields[2]);
            if (fields[3] === "1") {
              staffObj.isSuperuser('Yes');
            }
            staffObj.includeLine(true);
            staffObj.validLine(true);
            anyLinesIncluded = true;
          }
          if (!anyLinesIncluded) {
            this.bulkWarning(null);
            this.bulkError('This file contains no valid lines');
            return this.bulkStaff([]);
          }
        }, this);
        return reader.readAsText(file);
      };
      StaffListViewModel.prototype.bulkCreateStaff = function() {
        var settings, staff, uploadStaff, _i, _len, _ref;
        uploadStaff = [];
        _ref = this.bulkStaff();
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          staff = _ref[_i];
          if (staff.validLine() && staff.includeLine()) {
            uploadStaff.push(staff.line);
          }
        }
        console.log(uploadStaff);
        settings = {
          type: 'POST',
          url: '/api/v1/user/bulk/?format=json&always_return_data=true',
          data: JSON.stringify(uploadStaff),
          dataType: "json",
          processData: false,
          contentType: "application/json"
        };
        settings.success = __bind(function(data, textStatus, jqXHR) {
          var newData, staffTemp, _j, _len2, _ref2, _results;
          console.log("Batch staff created");
          console.log(data);
          console.log(textStatus);
          this.bulkStaff([]);
          this.bulkSuccess('Staff successfully uploaded!');
          this.bulkWarning(null);
          this.bulkError(null);
          _ref2 = data.objects;
          _results = [];
          for (_j = 0, _len2 = _ref2.length; _j < _len2; _j++) {
            newData = _ref2[_j];
            staffTemp = {
              user: newData,
              id: newData.id
            };
            staff = new Staff(staffTemp);
            console.log(staff);
            this.staff.push(staff);
            _results.push(this.bulkStaff.push(staff));
          }
          return _results;
        }, this);
        settings.error = __bind(function(jqXHR, textStatus, errorThrown) {
          console.log("Batch staff error");
          this.bulkWarning(null);
          return this.bulkError('An unexpected error occured');
        }, this);
        this.bulkAjaxInProgress(true);
        return $.ajax(settings);
      };
      StaffListViewModel.prototype.createStaff = function() {
        var newStaff, settings;
        newStaff = {
          first_name: this.newStaff.firstName(),
          last_name: this.newStaff.lastName(),
          is_superuser: this.newStaff.isSuperuser(),
          password: this.newStaff.password1()
        };
        if (newStaff.first_name === '') {
          this.newStaffError('First name cannot be empty');
          return;
        }
        if (newStaff.last_name === '') {
          this.newStaffError('Last name cannot be empty');
          return;
        }
        if (newStaff.password !== this.newStaff.password2()) {
          this.newStaffError('Passwords do not match');
          return;
        }
        if (newStaff.password.length < 4) {
          this.newStaffError('Password must be at least 4 characters');
          return;
        }
        settings = {
          type: 'POST',
          url: '/api/v1/user/add_user/?format=json&always_return_data=true',
          data: JSON.stringify(newStaff),
          dataType: "json",
          processData: false,
          contentType: "application/json"
        };
        settings.success = __bind(function(data, textStatus, jqXHR) {
          var staff;
          console.log("Staff successfully created!");
          staff = {
            user: data.object,
            id: data.object.id
          };
          this.staff.push(new Staff(staff));
          resizeAllCarousels();
          this.newStaffIsCreating(false);
          this.newStaffSuccess(("" + staff.user.first_name + " " + staff.user.last_name + " ") + ("has been created with the username " + staff.user.username));
          return this.newStaffError(false);
        }, this);
        settings.error = __bind(function(jqXHR, textStatus, errorThrown) {
          console.log("Staff not created!");
          this.newStaffAjaxLoad(false);
          return this.newStaffError('An unexpected error occured');
        }, this);
        this.newStaffAjaxLoad(true);
        return $.ajax(settings);
      };
      StaffListViewModel.prototype.addHousingGroup = function() {
        var data;
        try {
          console.log("adding HG " + this.newHousingGroup.housingGroup().name());
        } catch (TypeError) {
          return;
        }
        data = {};
        data.housing_group = ['/api/v1/housingGroup/' + this.newHousingGroup.housingGroup().id() + '/'];
        $.each(this.currentStaff().housingGroups(), __bind(function(index, value) {
          var hg;
          hg = $.isFunction(value) ? value() : value;
          if (data.housing_group.indexOf('api/v1/housingGroup/' + hg.id() + '/') === -1) {
            return data.housing_group.push('/api/v1/housingGroup/' + hg.id() + '/');
          }
        }, this));
        console.log(JSON.stringify(data));
        return $.ajax("/api/v1/staff/" + (this.currentStaff().id()) + "/?format=json", {
          data: JSON.stringify(data),
          dataType: "json",
          type: "PUT",
          contentType: "application/json",
          processData: false,
          success: __bind(function(result, status) {
            var newHG, target;
            console.log("added HG?!");
            console.log(status);
            newHG = new HousingGroup(null);
            target = this.newHousingGroup.housingGroup;
            newHG.id(target().id());
            newHG.name(target().name());
            newHG.staff(target().staff());
            newHG.resourceURI = target().resourceURI;
            newHG.animals(target().animals());
            return this.currentStaff().housingGroups.push(newHG);
          }, this),
          error: __bind(function(result) {
            return console.log(result);
          }, this)
        });
      };
      StaffListViewModel.prototype.deleteHousingGroup = function(hg) {
        var data, idToDelete, updatedGroupList, url;
        idToDelete = hg.id();
        url = "/api/v1/staff/" + (this.currentStaff().id()) + "/?format=json";
        updatedGroupList = [];
        $.each(this.currentStaff().housingGroups(), function(index, value) {
          var hgUrl;
          hgUrl = "/api/v1/housingGroup/" + (value.id()) + "/";
          if (value.id() !== idToDelete) {
            return updatedGroupList.push(hgUrl);
          }
        });
        data = {
          'housing_group': updatedGroupList
        };
        return $.ajax(url, {
          data: JSON.stringify(data),
          dataType: "json",
          type: "PUT",
          contentType: "application/json",
          processData: false,
          success: __bind(function(result) {
            console.log("removed HG");
            return this.currentStaff().housingGroups.remove(hg);
          }, this),
          error: __bind(function(result) {
            return console.log(result);
          }, this)
        });
      };
      StaffListViewModel.prototype.viewInfo = function(staff) {
        staff.loadInfo();
        $('#modal-staff-info').modal('show');
        return this.currentStaff(staff);
      };
      StaffListViewModel.prototype.load = function() {
        $.getJSON('/api/v1/staff/?format=json', __bind(function(data) {
          var mapped;
          mapped = $.map(data.objects, function(item) {
            return new Staff(item);
          });
          return this.staff(mapped);
        }, this));
        return $.getJSON('/api/v1/exhibit/?format=json', __bind(function(data) {
          var mapped;
          mapped = $.map(data.objects, function(item) {
            return new Exhibit(item);
          });
          return this.exhibits(mapped);
        }, this));
      };
      return StaffListViewModel;
    })();
    PawsViewModel = {
      AnimalListVM: new AnimalListViewModel(),
      EnrichmentListVM: new EnrichmentListViewModel(),
      ObservationListVM: new ObservationListViewModel(),
      StaffListVM: new StaffListViewModel()
    };
    ko.applyBindings(PawsViewModel.AnimalListVM, document.getElementById('animalListContainer'));
    ko.applyBindings(PawsViewModel.EnrichmentListVM, document.getElementById('enrichmentListContainer'));
    ko.applyBindings(PawsViewModel.ObservationListVM, document.getElementById('observationsContainer'));
    ko.applyBindings(PawsViewModel.StaffListVM, document.getElementById('staffContainer'));
    window.sammy = Sammy(__bind(function(context) {
      context.get('/', __bind(function() {
        $('#main > div:not(#home)').hide();
        PawsViewModel.EnrichmentListVM.empty();
        PawsViewModel.AnimalListVM.empty();
        $('#home').show();
        return resizeAllCarousels();
      }, this));
      context.get('/animals', __bind(function() {
        $('#main > div:not(#animalListContainer)').hide();
        PawsViewModel.EnrichmentListVM.empty();
        PawsViewModel.AnimalListVM.load();
        $('#animalListContainer').show();
        return resizeAllCarousels();
      }, this));
      context.get('/enrichments', __bind(function() {
        $('#main > div:not(#enrichmentListContainer)').hide();
        PawsViewModel.AnimalListVM.empty();
        PawsViewModel.EnrichmentListVM.load();
        $('#enrichmentListContainer').show();
        return resizeAllCarousels();
      }, this));
      context.get('/observe', __bind(function() {
        $('#main > div:not(#observationsContainer)').hide();
        PawsViewModel.AnimalListVM.empty();
        PawsViewModel.EnrichmentListVM.empty();
        PawsViewModel.ObservationListVM.load();
        $('#observationsContainer').show();
        return resizeAllCarousels();
      }, this));
      context.get('/staff', __bind(function() {
        $('#main > div:not(#staffContainer)').hide();
        PawsViewModel.AnimalListVM.empty();
        PawsViewModel.EnrichmentListVM.empty();
        PawsViewModel.ObservationListVM.empty();
        PawsViewModel.StaffListVM.load();
        return $('#staffContainer').show();
      }, this));
      return context.get('/auth/logout', __bind(function() {
        return window.location = '/auth/logout';
      }, this));
    }, this));
    sammy.run();
    /*
      console.log PawsViewModel.ObservationListVM.observations
      console.log PawsViewModel.ObservationListVM.observations()
      $.each PawsViewModel.ObservationListVM.observations(), (obs) ->
        console.log "in"
        console.log obs
        obs.animal_observations.indirectUse.subscribe (value) ->
          console.log this
          console.log value 
          console.log "observation array changed"
          */
    MAX_SCROLLER_ROWS = 3;
    window.scrollers = {};
    resizeCarousel = function(scroller, numRows, fixedWidth) {
      var length, newWidth, oldWidth, singleWidth;
      if (numRows == null) {
        numRows = 1;
      }
      if (fixedWidth == null) {
        fixedWidth = true;
      }
      oldWidth = $(scroller).width();
      length = $(scroller).find('ul li').length;
      newWidth = 0;
      if (fixedWidth) {
        console.log("fixed");
        singleWidth = $(scroller).find('ul li:first').outerWidth(true);
        newWidth = Math.ceil(length / numRows) * singleWidth;
        while (newWidth > 8000) {
          numRows++;
          newWidth = Math.ceil(length / numRows) * singleWidth;
        }
      } else {
        $(scroller).find('ul li').each(function() {
          return newWidth += $(this).outerWidth(true);
        });
        newWidth /= numRows;
        if (newWidth > 8000) {
          newWidth = 8000;
        }
        console.log(newWidth);
      }
      if (newWidth !== oldWidth) {
        console.log('Resizing carousel from ' + oldWidth + ' to ' + newWidth + ' with ' + numRows + ' rows');
        $(scroller).width(newWidth);
        return true;
      }
      return false;
    };
    resizeAllCarousels = function(refresh) {
      if (refresh == null) {
        refresh = true;
      }
      $('.carousel-scroller').each(function() {
        var numRows, resized;
        if ($(this).hasClass('carousel-rows')) {
          numRows = Math.min(Math.floor(($(window).height() - $(this).parent().offset().top) / $(this).find('li:first').outerHeight(true)), MAX_SCROLLER_ROWS);
          console.log("numrows: " + numRows);
        } else {
          numRows = 1;
        }
        resized = resizeCarousel(this, numRows, $(this).hasClass('carousel-fixed-width'));
        if (refresh && resized) {
          console.log('Refreshing carousel');
          return $.each(scrollers, function(key, value) {
            return value.refresh();
          });
        }
      });
      return $('.list-vertical').each(function() {
        return $.each(scrollers, function(key, value) {
          return value.refresh();
        });
      });
    };
    scrollers.categorySelector = new iScroll('categorySelector', {
      vScroll: false,
      momentum: true,
      bounce: true,
      hScrollbar: false
    });
    scrollers.subcategorySelector = new iScroll('subcategorySelector', {
      vScroll: false,
      momentum: true,
      bounce: true,
      hScrollbar: false
    });
    scrollers.enrichmentSelector = new iScroll('enrichmentSelector', {
      vScroll: false,
      momentum: true,
      bounce: true,
      hScrollbar: false
    });
    scrollers.observationEnrichments = new iScroll('observationEnrichments', {
      vScroll: true,
      hScroll: false,
      momentum: true,
      bounce: true,
      vScrollbar: true
    });
    $(window).resize(function() {
      clearTimeout(window.resizeTimeout);
      return window.resizeTimeout = setTimeout(resizeAllCarousels, 500);
    });
    $('#animal-modal').modal({
      show: false
    });
    return $(".alert").alert();
  });
}).call(this);
