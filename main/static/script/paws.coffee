$(document).ready ->
  unless Date::toISOString
    pad = (number) ->
      r = String(number)
      r = "0" + r  if r.length is 1
      r
    Date::toISOString = ->
      @getUTCFullYear() + "-" + pad(@getUTCMonth() + 1) + "-"
      + pad(@getUTCDate()) + "T" + pad(@getUTCHours()) + ":"
      + pad(@getUTCMinutes()) + ":" + pad(@getUTCSeconds()) + "."
      + String((@getUTCMilliseconds() / 1000).toFixed(3)).slice(2, 5) + "Z"

  # Knockout
  # ###############
  updateAnimalObservation = new ko.subscribable()

  # Models
  # ----------------
  class Animal
    constructor: (data) ->
      @name = ko.observable data.name
      @id = ko.observable data.id
      @speciesCommonName = ko.observable data.species.common_name
      @speciesId = ko.observable data.species.id
      @speciesScientificName = ko.observable data.species.scientific_name
      @active = ko.observable false
      @observation = ko.observable null

  class AnimalObservation
    constructor: (data=null) ->
      if data?
        @id = data.id
        @animal = ko.observable new Animal data.animal
        @observation_id = ko.observable data.observation.id
        @interaction_time = ko.observable data.interaction_time
        @observation_time = ko.observable data.observation_time
        @indirect_use = ko.observable data.indirect_use
        @behavior = ko.observable data.behavior

        @interaction_time.subscribe (value) =>
          console.log "change interaction_time"
          d =
            id: @id
            value: value
            type: "interaction_time"
          console.log d
          updateAnimalObservation.notifySubscribers d, "saveAnimalObservation"
        @observation_time.subscribe (value) =>
          console.log "change observation_time"
          d =
            id: @id
            value: value
            type: "observation_time"
          console.log d
          updateAnimalObservation.notifySubscribers d, "saveAnimalObservation"
        @indirect_use.subscribe (value) =>
          console.log "change indirect_use"
          d =
            id: @id
            value: value
            type: "indirect_use"
          console.log d
          updateAnimalObservation.notifySubscribers d, "saveAnimalObservation"
      else
        @id = ko.observable null
        @animal = ko.observable null
        @observation_id = ko.observable null
        @interaction_time = ko.observable null
        @observation_time = ko.observable null
        @indirect_use = ko.observable null
        @behavior = ko.observable null

  class Exhibit
    constructor: (data) ->
      @code = ko.observable data.code
      @housingGroups = ko.observableArray $.map data.housing_groups, (item) ->
        return new HousingGroup item
      @fullName = ko.computed =>
        return 'Exhibit ' + @code()
      @numOwned = ko.computed =>
        num = 0
        $.each @housingGroups(), (index, val) =>
          num++ if val.isInStaff()
        return num
      @resourceURI = data.resource_uri

  class HousingGroup
    constructor: (data) ->
      if data?
        @id = ko.observable data.id
        @name = ko.observable data.name
        @staff = ko.observableArray data.staff
        @resourceURI = data.resource_uri
        @animals = ko.observableArray $.map data.animals, (item) ->
          return new Animal item
      else
        @id = ko.observable null
        @name = ko.observable null
        @staff = ko.observableArray null
        @resourceURI = null
        @animals = ko.observableArray null

      @isInStaff = ko.computed =>
        if @staff()?
          return (@staff.indexOf('/api/v1/staff/' + window.userId + '/') != -1)
        else
          return false

  class Category
    constructor: (data={}) ->
      @name = ko.observable data.name
      @id = ko.observable data.id

  class Enrichment
    constructor: (data) ->
      if data?
        @id = ko.observable data.id
        @name = ko.observable data.name # non-observable is fine
        @categoryId = ko.observable data.subcategory.category.id
        @categoryName = ko.observable data.subcategory.category.name
        @subcategoryId = ko.observable data.subcategory.id
        @subcategoryName = ko.observable data.subcategory.name
        @count = ko.observable 0
        @disabled = false
      else
        @id = ko.observable null
        @name = ko.observable null
        @categoryId = ko.observable null
        @categoryName = ko.observable null
        @subcategoryId = ko.observable null
        @subcategoryName = ko.observable null
        @count = ko.observable 0
        @disabled = false

  class EnrichmentNote
    constructor: (data) ->
      if data?
        @enrichmentId = ko.observable data.enrichment.id
        @speciesCommonName = ko.observable data.species.common_name
        @speciesId = ko.observable data.species.id
        @speciesScientificName = ko.observable data.species.scientific_name
        @species = ko.observable new Species data.species
        @limitations = ko.observable data.limitations
        @instructions = ko.observable data.instructions
      else
        @enrichmentId = ko.observable null
        @speciesCommonName = ko.observable null
        @speciesId = ko.observable null
        @speciesScientificName = ko.observable null
        @species = ko.observable new Species null
        @limitations = ko.observable null
        @instructions = ko.observable null

  class Observation
    constructor: (data=null) ->
      if data?
        @id = data.id
        @enrichment = ko.observable data.enrichment # not using .name for now
        @animal_observations = ko.observableArray $.map data.animal_observations, (item) ->
          return new AnimalObservation item
        @date_created = ko.observable data.date_created
        @date_finished = ko.observable data.date_finished
      else
        @id = null
        @enrichment = ko.observable null
        @animal_observations = ko.observableArray []
        @date_created = ko.observable null
        @date_finished = ko.observable null
    modalTitle: () ->
      length = @animal_observations().length
      pluralized = if length > 1 then ' animals' else ' animal'
      return 'Observing ' + length + pluralized

  class Staff
    constructor: (data) ->
      @id = ko.observable data.id
      @first_name = ko.observable data.user.first_name
      @last_name = ko.observable data.user.last_name
      @username = ko.observable data.user.username
      @full_name = ko.computed =>
        return @first_name() + ' ' + @last_name()
      @animal_title = ko.computed =>
        return @full_name() + '\'s animals'
      @housingGroups = ko.observableArray []
      @loading = ko.observable false
      @is_superuser = ko.observable data.user.is_superuser
    loadInfo: () ->
      if @housingGroups().length != 0
        return
      # Get housing groups
      @loading true
      $.getJSON '/api/v1/housingGroup/?format=json&staff_id=' + @id(), (data) =>
        mapped = $.map data.objects, (item) ->
          return new HousingGroup item
        @housingGroups mapped
        @loading false

  class Species
    constructor: (data) ->
      if data?
        @commonName = ko.observable data.common_name
        @scientificName = ko.observable data.scientific_name
        @id = ko.observable data.id
        @resourceURI = data.resource_uri
      else
        @commonName = ko.observable null
        @scientificName = ko.observable null
        @id = ko.observable null


  class Subcategory
    constructor: (data) ->
      if data?
        @name = ko.observable data.name
        @id = ko.observable data.id
        @categoryId = ko.observable data.category.id
      else
        @name = ko.observable ''
        @id = ko.observable ''
        @categoryId = ko.observable ''
      @count = ko.observable 0

  # ViewModels
  # ----------------
  class AnimalListViewModel
    constructor: () ->
      # Arrays for holding data
      @animals = ko.observableArray []
      @species = ko.observableArray []
      @exhibits = ko.observableArray []
      @categories = ko.observableArray []
      @subcategories = ko.observableArray []
      @enrichments = ko.observableArray []
      @enrichmentNotes = ko.observableArray []

      # Current filter variables
      @currentSpecies = ko.observable ''
      @currentEnrichment = ko.observable null

      # Making new
      @newObservationAjaxLoad = ko.observable false
      @newObservationError = ko.observable null
      @newObservationIsCreating = ko.observable false
      @newObservationSuccess = ko.observable false

      # Making new
      @newAnimalObservationAjaxLoad = ko.observable false
      @newAnimalObservationError = ko.observable null
      @newAnimalObservationIsCreating = ko.observable false
      @newAnimalObservationSuccess = ko.observable false

      # Staff that's in charge of animals
      @staffs = ko.observableArray []

      # If viewing all keeper's animals or just yours
      @viewAll = ko.observable false
      @viewText = ko.computed =>
        if @viewAll()
          return 'All Animals'
        else
          return 'Your Animals'

      # Compute the filtered lists
      @filterAnimalsBySpecies = ko.computed =>
        species = @currentSpecies()
        if species == ''
          return @animals()
        return ko.utils.arrayFilter @animals(), (animal) ->
          return animal.speciesId() == species.id()

      # Enrichment application
      # Current animal selection(s), the animals themselves
      @selectedAnimals = ko.observableArray []

      # checks to see if animals changed
      @selectedAnimalsChanged = false

      # Title for observation modal dialog
      @modalTitleEnrichment = ko.computed =>
        length = @selectedAnimals().length
        pluralized = if length != 1 then ' animals' else ' animal'
        return 'Select Enrichment - Observing ' + length + pluralized

      # Title for observation modal dialog
      @modalTitleAnimal = ko.computed =>
        length = @selectedAnimals().length
        pluralized = if length != 1 then ' animals' else ' animal'
        enrichName = if @currentEnrichment()? then @currentEnrichment().name() + ' - ' else ''
        return enrichName + 'Observing ' + length + pluralized

      # Observation stuff
      @observation = ko.observable new Observation()

      # Current Filters
      @categoryFilter = ko.observable ''
      @subcategoryFilter = ko.observable ''

      @behaviorType = [
        { id: -2, type: 'Avoid'}
        { id: -1, type: 'Negative'}
        { id: 0, type: 'N/A'}
        { id: 1, type: 'Positive'}
      ]

      @subcategoriesFilterCategory = ko.computed =>
        category = @categoryFilter()
        if category == ''
          return []
        return ko.utils.arrayFilter @subcategories(), (subcategory) ->
          return subcategory.categoryId() == category.id()

      @enrichmentsFilterCategory = ko.computed =>
        category = @categoryFilter()
        if category == ''
          return @enrichments()
        return ko.utils.arrayFilter @enrichments(), (enrichment) ->
          return enrichment.categoryId() == category.id()
          
      @enrichmentsFilterSubcategory = ko.computed =>
        subcategory = @subcategoryFilter()
        if subcategory == ''
          return @enrichmentsFilterCategory()
        return ko.utils.arrayFilter @enrichmentsFilterCategory(), (enrichment) ->
          return enrichment.subcategoryId() == subcategory.id()

      # Creation fields.
      # Species creation
      @newSpecies =
        commonName: ko.observable ''
        scientificName: ko.observable ''
      @newSpeciesError = ko.observable null
      @newSpeciesWarning = ko.observable null
      @newSpeciesSuccess = ko.observable false
      @newSpeciesIsCreating = ko.observable true
      @newSpeciesAjaxLoad = ko.observable false

      # Exhibit creation
      @newExhibit =
        code: ko.observable ''
      @newExhibitError = ko.observable null
      @newExhibitWarning = ko.observable null
      @newExhibitSuccess = ko.observable false
      @newExhibitIsCreating = ko.observable true
      @newExhibitAjaxLoad = ko.observable false

      # HousingGroup creation
      @newHousingGroup =
        name: ko.observable ''
        exhibit: ko.observable ''
      @newHousingGroupError = ko.observable null
      @newHousingGroupWarning = ko.observable null
      @newHousingGroupSuccess = ko.observable false
      @newHousingGroupIsCreating = ko.observable true
      @newHousingGroupAjaxLoad = ko.observable false

      # Animal creation
      @newAnimal =
        count: ko.observable '1'
        housingGroup: ko.observable ''
        name: ko.observable ''
        species: ko.observable ''
        exhibit: ko.observable {
          housingGroups: ko.observableArray []
        }
      @newAnimalError = ko.observable null
      @newAnimalWarning = ko.observable null
      @newAnimalSuccess = ko.observable false
      @newAnimalIsCreating = ko.observable true
      @newAnimalAjaxLoad = ko.observable false

      # Bulk upload fields
      @uploadDisableSubmit = ko.observable true
      @uploadEnablePreview = ko.observable false
      @uploadAnimals = []
      @uploadAnimalsPreview = ko.observableArray []
      @uploadErrorMessageBody = ko.observable ''
      @uploadErrorMessageEnable = ko.observable false
      @uploadWarningMessageBody = ko.observable ''
      @uploadWarningMessageEnable = ko.observable false
      @uploadAjaxInProgress = ko.observable false
      @uploadUploadSuccess = ko.observable false
      @uploadIncludeFirstLine = ko.observable true

      # Must bind this to self because we need to access @files[0] within the
      # callback function.
      self = this
      document.getElementById('file_upload').onchange = ->
        file = @files[0]
        console.log file
        self.uploadDisableSubmit true
        self.uploadEnablePreview false
        self.uploadErrorMessageEnable false
        self.uploadWarningMessageEnable false
        reader = new FileReader()
        console.log reader
        reader.onload = (ev) ->

          if (ev.target.result == "")
            self.uploadErrorMessageEnable true
            self.uploadErrorMessageBody 'The file is empty'
            return

          # Split the lines up and reset the arrays.
          lines = ev.target.result.split /[\n|\r]/
          self.uploadAnimals = []
          self.uploadAnimalsPreview []
          # Line format:
          # ID,CommonName,ScientificName,Exhibit,HouseGroupName,HouseName,Count
          for line, i in lines
            fields = line.split(',')
            console.log i
            console.log fields

            if (fields.length == 0)
              console.log "The line is empty"
              continue

            # Make sure there are only 7 fields
            if (fields.length != 7)
              if (not self.uploadWarningMessageEnable())
                self.uploadWarningMessageEnable true
                self.uploadWarningMessageBody(
                    "Line #{i + 1}: has #{fields.length} fields")
              continue

            # Make sure there's an integer in this field.
            if (not parseInt fields[0])
              if (not self.uploadWarningMessageEnable())
                self.uploadWarningMessageEnable true
                self.uploadWarningMessageBody(
                    "Line #{i + 1}: ID must be an integer (\"#{fields[0]}\")")
              continue

            # Make sure there's an integer in this field too.
            if (not parseInt fields[6])
              if (not self.uploadWarningMessageEnable())
                self.uploadWarningMessageEnable true
                self.uploadWarningMessageBody(
                    "Line #{i + 1}: Count must be an integer (\"#{fields[6]}\")")
              continue

            # Make sure fields are all good.
            hasBlankField = false
            for field in fields
              if (field == "")
                console.log "field is bad!"
                hasBlankField = true
                break

            if (hasBlankField)
              if (not self.uploadWarningMessageEnable())
                self.uploadWarningMessageEnable true
                self.uploadWarningMessageBody(
                    "Line #{i + 1} has blank fields and has been excluded.")
              continue

            # Add line to URL.
            self.uploadAnimals.push line
            self.uploadAnimalsPreview.push {
              id: fields[0]
              speciesCommonName: fields[1]
              speciesScientificName: fields[2]
              exhibit: fields[3]
              houseGroupName: fields[4]
              houseName: fields[5]
              count: fields[6]
            }

          if (self.uploadAnimals.length > 0)
            # Show table.
            self.uploadDisableSubmit false
            self.uploadEnablePreview true
          else
            self.uploadWarningMessageEnable false
            self.uploadErrorMessageEnable true
            self.uploadErrorMessageBody(
                "#{file.name} is not in the proper format")
        
        # Initiate the reader.
        reader.readAsText(file)

    openCreateSpecies: () ->
      @newSpecies.commonName ''
      @newSpecies.scientificName ''
      @newSpeciesError null
      @newSpeciesWarning null
      @newSpeciesSuccess false
      @newSpeciesIsCreating true
      @newSpeciesAjaxLoad false

    createNewSpecies: () =>
      newSpecies =
        common_name: @newSpecies.commonName()
        scientific_name: @newSpecies.scientificName()

      # Make some simple checks.
      if (newSpecies.common_name.length == 0)
        @newSpeciesError 'Common Name cannot be empty'
        return
      if (newSpecies.scientific_name.length == 0)
        @newSpeciesError 'Scientific Name cannot be empty'
        return
      if (newSpecies.common_name.length > 100)
        @newSpeciesError 'Common Name cannot more than 100 characters'
        return
      if (newSpecies.scientific_name.length > 200)
        @newSpeciesError 'Scientific Name cannot be more than 200 characters'
        return

      settings =
        type: 'POST'
        url: '/api/v1/species/?format=json'
        data: JSON.stringify newSpecies
        dataType: "json",
        processData:  false,
        contentType: "application/json"

      settings.success = (data, textStatus, jqXHR) =>
        console.log "New Species created"
        console.log data
        console.log textStatus

        # Show success message.
        @newSpeciesSuccess "Species #{newSpecies.common_name} " +
            "(#{newSpecies.scientific_name}) was created"
        @newSpeciesError null
        @newSpeciesAjaxLoad false

        # TODO(mark): Need to add successful object to species list.
        @species new Species data

      settings.error = (jqXHR, textStatus, errorThrown) =>
        console.log "Species error"
        @newSpeciesError 'An unexpected error occured'
        @newSpeciesAjaxLoad false

      # Make the ajax call.
      @newSpeciesAjaxLoad true
      $.ajax settings

    openCreateExhibit: () ->
      @newExhibit.code ''
      @newExhibitError null
      @newExhibitWarning null
      @newExhibitSuccess false
      @newExhibitIsCreating true
      @newExhibitAjaxLoad false

    createNewExhibit: () =>
      newExhibit =
        code: @newExhibit.code()

      # Make some simple checks.
      if (newExhibit.code.length == 0)
        @newExhibitError 'Code cannot be empty'
        return
      if (newExhibit.code.length > 100)
        @newExhibitError 'Code cannot more than 100 characters'
        return

      settings =
        type: 'POST'
        url: '/api/v1/exhibit/?format=json'
        data: JSON.stringify newExhibit
        dataType: "json",
        processData:  false,
        contentType: "application/json"

      settings.success = (data, textStatus, jqXHR) =>
        console.log "New Exhibit created"
        console.log data
        console.log textStatus

        # Show success message.
        @newExhibitSuccess "Exhibit #{newExhibit.code} was created"
        @newExhibitError null
        @newExhibitAjaxLoad false

        # TODO(mark): Need to add successful object to exhibit list.
        @exhibits.push new Exhibit data

      settings.error = (jqXHR, textStatus, errorThrown) =>
        console.log "Create exhibit error"
        @newExhibitError 'An unexpected error occured'
        @newExhibitAjaxLoad false

      # Make the ajax call.
      @newExhibitAjaxLoad true
      $.ajax settings

    openCreateHousingGroup: () ->
      @newHousingGroup.name ''
      @newHousingGroup.exhibit ''
      @newHousingGroupError null
      @newHousingGroupWarning null
      @newHousingGroupSuccess false
      @newHousingGroupIsCreating true
      @newHousingGroupAjaxLoad false

    createNewHousingGroup: () =>
      newHousingGroup =
        name: @newHousingGroup.name()
        exhibit: @newHousingGroup.exhibit().resourceURI
      console.log newHousingGroup

      # Make some simple checks.
      if (newHousingGroup.name.length == 0)
        @newHousingGroupError 'Name cannot be empty'
        return
      if (newHousingGroup.name.length > 100)
        @newHousingGroupError 'Name cannot more than 100 characters'
        return

      settings =
        type: 'POST'
        url: '/api/v1/housingGroup/?format=json'
        data: JSON.stringify newHousingGroup
        dataType: "json",
        processData:  false,
        contentType: "application/json"

      settings.success = (data, textStatus, jqXHR) =>
        console.log "New HousingGroup created"
        console.log data
        console.log textStatus

        # Show success message.
        @newHousingGroupSuccess "HousingGroup #{newHousingGroup.name} " +
            "for exhibit #{@newHousingGroup.exhibit().code()} was created"
        @newHousingGroupError null
        @newHousingGroupAjaxLoad false

        # TODO(mark): Need to add successful object to housinggroup list.
        @newHousingGroup.exhibit().housingGroups.push new HousingGroup data

      settings.error = (jqXHR, textStatus, errorThrown) =>
        console.log "Create housinggroup error"
        @newHousingGroupError 'An unexpected error occured'
        @newHousingGroupAjaxLoad false

      # Make the ajax call.
      @newHousingGroupAjaxLoad true
      $.ajax settings

    openCreateAnimal: () ->
      @newAnimal.count '1'
      @newAnimal.housingGroup ''
      @newAnimal.name ''
      @newAnimal.species ''
      @newAnimal.exhibit {
        housingGroups: ko.observableArray []
      }
      @newAnimalError null
      @newAnimalWarning null
      @newAnimalSuccess false
      @newAnimalIsCreating true
      @newAnimalAjaxLoad false

    createNewAnimal: () =>
      newAnimal =
        count: parseInt @newAnimal.count()
        housing_group: @newAnimal.housingGroup().resourceURI
        name: @newAnimal.name()
        species: @newAnimal.species().resourceURI

      # Make some simple checks.
      if (@newAnimal.count().length == 0)
        @newAnimalError 'Count cannot be empty'
        return
      if (newAnimal.count <= 0)
        @newAnimalError 'Count must be a positive integer'
        return
      if (!newAnimal.count)
        @newAnimalError 'Count must be a number'
        return
      if (newAnimal.name.length == 0)
        @newAnimalError 'Name cannot be empty'
        return
      if (newAnimal.name.length > 100)
        @newAnimalError 'Name cannot more than 100 characters'
        return

      settings =
        type: 'POST'
        url: '/api/v1/animal/?format=json'
        data: JSON.stringify newAnimal
        dataType: "json",
        processData:  false,
        contentType: "application/json"

      settings.success = (data, textStatus, jqXHR) =>
        console.log "New Animal created"
        console.log data
        console.log textStatus

        # Show success message.
        @newAnimalSuccess "Animal #{newAnimal.name} was created"
        @newAnimalError null
        @newAnimalAjaxLoad false

        # TODO(mark): Need to add successful object to animal list.
        @newAnimal.housingGroup().animals.push new Animal data

      settings.error = (jqXHR, textStatus, errorThrown) =>
        console.log "Create animal error"
        @newAnimalError 'An unexpected error occured'
        @newAnimalAjaxLoad false

      # Make the ajax call.
      @newAnimalAjaxLoad true
      $.ajax settings

    # Open info modal
    openInfo: () ->
      # Empty out staff array
      @staffs []
      $.each @selectedAnimals(), (index, animal) =>
        console.log animal
        # Get data from API
        $.getJSON "/api/v1/staff/?format=json&animal_id=#{animal.id()}", (data) =>
          # Push each staff into 
          $.each data.objects, (index, item) =>
            @staffs.push (new Staff item)
      $('#modal-animal-info').modal('show')

    # Open bulk upload.
    openBulkUpload: () ->
      $('#file_upload').val('');
      @uploadDisableSubmit true
      @uploadEnablePreview false
      @uploadAnimals = []
      @uploadAnimalsPreview []
      @uploadErrorMessageEnable false
      @uploadWarningMessageEnable false
      @uploadAjaxInProgress false
      @uploadUploadSuccess false
      @uploadIncludeFirstLine true

    sendBulkUpload: () ->
      uploadAnimals = @uploadAnimals

      # Don't include the first line if the user doesn't want us to.
      if (not @uploadIncludeFirstLine())
        uploadAnimals = uploadAnimals.slice 1, uploadAnimals.length

      settings =
        type: 'POST'
        url: '/api/v1/animal/bulk/?format=json'
        data: JSON.stringify uploadAnimals
        dataType: "json",
        processData:  false,
        contentType: "application/json"

      settings.success = (data, textStatus, jqXHR) =>
        console.log "Batch animals created"
        console.log data
        console.log textStatus

        # Show success message.
        @uploadUploadSuccess true
        @uploadErrorMessageEnable false
        @uploadWarningMessageEnable false

        # Reload to ensure that we have all animals added.
        @load()

      settings.error = (jqXHR, textStatus, errorThrown) =>
        console.log "Batch animals error"
        @uploadErrorMessageEnable true
        @uploadWarningMessageEnable false
        @uploadErrorMessageBody 'An unexpected error occured'
        @uploadAjaxInProgress false

      # Make the ajax call.
      @uploadAjaxInProgress true
      $.ajax settings

    # Toggle viewAll
    toggleViewAll: () =>
      @viewAll !@viewAll()

    # Apply filters
    filterCategory: (category) =>
      if category == @categoryFilter()
        @subcategoryFilter('')
        @categoryFilter('')
      else
        @subcategoryFilter('')
        @categoryFilter(category)
      resizeAllCarousels()

    filterSubcategory: (subcategory) =>
      if subcategory == @subcategoryFilter()
        @subcategoryFilter('')
      else
        @subcategoryFilter(subcategory)
      resizeAllCarousels()
      ## For disable instead of remove, need css rule, not working
      #ko.utils.arrayForEach @enrichments(), (enrichment) ->
      #  if enrichment.subcategoryId() != subcategory.id()
      #    enrichment.disabled = true
      #  else
      #    enrichment.disabled = false

    # Apply filters
    setCurrentSpecies: (species) =>
      if species == @currentSpecies()
        @currentSpecies('')
      else
        @currentSpecies(species)
      resizeAllCarousels()

    # Boolean, animal is selected
    isSelected: (animal) =>
      return animal.active()

    # Add animal to selected object
    selectAnimal: (animal) =>
      @selectedAnimalsChanged = true
      animal.active true
      @selectedAnimals.push animal

    # Remove animal from selected object
    deselectAnimal: (animal) =>
      animal.active false
      @selectedAnimals.remove animal

    # Toggle a single animal's state
    toggleAnimal: (animal) =>
      if !@isSelected(animal)
        @selectAnimal(animal)
      else
        @deselectAnimal(animal)

    # Select animal(s) functions
    selectExhibit: (exhibit) =>
      selectAnimals = []
      deselectAnimals = []
      $.each exhibit.housingGroups(), (i, hg) =>
        $.each hg.animals(), (index, animal) =>
          if !@isSelected(animal)
            selectAnimals.push animal
          else
            deselectAnimals.push animal
      if selectAnimals.length > 0
        $.each selectAnimals, (index, animal) =>
          @selectAnimal(animal)
      else # Deselect all animals in exhibit if already fully selected
        $.each deselectAnimals, (index, animal) =>
          @deselectAnimal(animal)

    selectHousingGroup: (housingGroup) =>
      selectAnimals = []
      deselectAnimals = []
      $.each housingGroup.animals(), (index, animal) =>
        if !@isSelected(animal)
          selectAnimals.push animal
        else
          deselectAnimals.push animal
      if selectAnimals.length > 0
        $.each selectAnimals, (index, animal) =>
          @selectAnimal(animal)
      else # Deselect all animals in exhibit if already fully selected
        $.each deselectAnimals, (index, animal) =>
          @deselectAnimal(animal)

    # Make a new observation
    # Observations are stored in the Animal
    newObservation: () =>
      if @selectedAnimalsChanged
        $.each @selectedAnimals(), (index, animal) =>
          # Initialize new observation if it doesn't exist
          if @selectedAnimals()[index].observation() == null
            @selectedAnimals()[index].observation new AnimalObservation()
        # Load enrichments for active species
        @loadEnrichments()
      @selectedAnimalsChanged = false

    selectEnrichment: (enrichment) =>
      @currentEnrichment enrichment

    # Load exhibits and animals
    load: () =>
      # Get data from API
      $.getJSON '/api/v1/exhibit/?format=json&limit=0', (data) =>
        mappedExhibits = $.map data.objects, (item) ->
          return new Exhibit item
        @exhibits mappedExhibits
      $.getJSON '/api/v1/species/?format=json&limit=0', (data) =>
        mappedSpecies = $.map data.objects, (item) ->
          return new Species item
        @species ko.toJS mappedSpecies

    # Check if ID exists in observableArray
    idInArray: (id, array) =>
      retval = false
      $.each array, (index, value) =>
        if id == value.id()
          retval = true
          return false # break
      return retval

    # Load enrichments based on the species that are selected
    loadEnrichments: () =>
      # Build the species set
      speciesSet = {}
      $.each @selectedAnimals(), (index, animal) =>
        speciesSet[animal.speciesId()] = true

      # For each item in species set, add that to the url
      url = '/api/v1/enrichmentNote/?format=json&limit=0&species_id='
      $.each speciesSet, (key, value) =>
        url += key + ','

      # Empty out the arrays before we begin
      @enrichmentNotes []
      @enrichments [] 
      @subcategories []
      @categories []
      @currentEnrichment null

      # Get teh data
      $.getJSON url, (data) =>
        mappedEnrichmentNotes = $.map data.objects, (item) =>
          # Create a new enrichmentNote to store everything in
          enrichmentNote = new EnrichmentNote item

          # Create a new Enrichment, push if it's not in array already
          tempEnrichment = new Enrichment item.enrichment
          @enrichments.push tempEnrichment if !@idInArray tempEnrichment.id(), @enrichments()

          # Create a new Subcategory, push if it's not in array already
          tempSubcategory = new Subcategory item.enrichment.subcategory
          @subcategories.push tempSubcategory if !@idInArray tempSubcategory.id(), @subcategories()
          # Create a new Category, push if it's not in array already

          tempCategory = new Category item.enrichment.subcategory.category
          @categories.push tempCategory if !@idInArray tempCategory.id(), @categories()
          return enrichmentNote

        @enrichmentNotes mappedEnrichmentNotes
        @enrichments.sort (a, b) ->
          if a.name() == b.name()
            return 0
          else if a.name() < b.name()
            return -1
          else
            return 1

        resizeAllCarousels()

    createObservation: () =>
      newObservation =
        enrichment: '/api/v1/enrichment/' + @currentEnrichment().id() + '/'
        staff: '/api/v1/enrichment/' + window.userId + '/'
        date_created: new Date().toISOString().split('.')[0]

      # Make sure we are not in the middle of loading.
      if (@newObservationAjaxLoad())
        console.log "We are already trying to send something"
        return false

      # Validate fields before continuing.

      settings =
        type: 'POST'
        url: '/api/v1/observation/?format=json'
        data: JSON.stringify newObservation
        dataType: "json",
        processData:  false,
        contentType: "application/json"

      settings.success = (data, textStatus, jqXHR) =>
        console.log "Observation successfully created!"
        console.log jqXHR.getResponseHeader 'Location'

        # Extract the category id from the Location response header.
        locationsURL = jqXHR.getResponseHeader 'Location'
        pieces = locationsURL.split "/"
        newObservation.id = pieces[pieces.length - 2]

        # Show success message and remove extra weight.
        @newObservationIsCreating false
        @newObservationSuccess true
        @newObservationError null

        console.log newObservation

        @createAnimalObservation(newObservation.id)

        @newObservationAjaxLoad false

        $.each @selectedAnimals(), (index, animal) =>
          animal.active false
        @currentEnrichment null

        # (optional) redirect
        $('#modal-observe-1').modal('hide').on 'hidden', ->
          sammy.setLocation('/observe')

      settings.error = (jqXHR, textStatus, errorThrown) =>
        console.log "Observation not created!"
        @newObservationNameErrorMessage true
        @newObservationAjaxLoad false
        @newObservationNameMessageBody 'An unexpected error occured'

      # Make the ajax call.
      @newObservationAjaxLoad true
      $.ajax settings    

    createAnimalObservation: (observationId) =>
      for animal in @selectedAnimals()
        newAnimalObservation =
          animal: '/api/v1/animal/' + animal.id() + '/'
          observation: '/api/v1/observation/' + observationId + '/'

        # Validate fields before continuing.

        settings =
          type: 'POST'
          url: '/api/v1/animalObservation/?format=json'
          data: JSON.stringify newAnimalObservation
          dataType: "json",
          processData:  false,
          contentType: "application/json"

        settings.success = (data, textStatus, jqXHR) =>
          console.log "Animalobservation successfully created!"

          # Extract the category id from the Location response header.
          locationsURL = jqXHR.getResponseHeader 'Location'
          pieces = locationsURL.split "/"
          newAnimalObservation.id = pieces[pieces.length - 2]

          # Show success message and remove extra weight.
          @newAnimalObservationIsCreating false
          @newAnimalObservationSuccess true
          @newAnimalObservationError null

          console.log newAnimalObservation

        settings.error = (jqXHR, textStatus, errorThrown) =>
          console.log "Animalobservation not created!"
          @newAnimalObservationNameErrorMessage true
          @newAnimalObservationNameMessageBody 'An unexpected error occured'

        # Make the ajax call.
        $.ajax settings


    # Clear everything out
    empty: () =>
      @animals []
      @exhibits []
      @categories []
      @subcategories []
      @enrichments []
      @enrichmentNotes []
      @currentSpecies ''

  class EnrichmentListViewModel
    constructor: () ->
      @categories = ko.observableArray []
      @subcategories = ko.observableArray []
      @enrichments = ko.observableArray []
      @species = ko.observableArray []

      # Operations
      # Current Filters
      @categoryFilter = ko.observable ''
      @subcategoryFilter = ko.observable ''

      # Filtered lists
      @subcategoriesFilterCategory = ko.computed =>
        category = @categoryFilter()
        if category == ''
          return []
        return ko.utils.arrayFilter @subcategories(), (subcategory) ->
          return subcategory.categoryId() == category.id()

      @enrichmentsFilterCategory = ko.computed =>
        category = @categoryFilter()
        if category == ''
          return @enrichments()
        return ko.utils.arrayFilter @enrichments(), (enrichment) ->
          return enrichment.categoryId() == category.id()

      @enrichmentsFilterSubcategory = ko.computed =>
        subcategory = @subcategoryFilter()
        if subcategory == ''
          return @enrichmentsFilterCategory()
        return ko.utils.arrayFilter @enrichmentsFilterCategory(), (enrichment) ->
          return enrichment.subcategoryId() == subcategory.id()

      # Category Creation fields.
      @newCategory =
        name: ko.observable ''
      @newCategoryNameErrorMessage = ko.observable false
      @newCategoryNameSuccessMessage = ko.observable false
      @newCategoryNameMessageBody = ko.observable ''
      @newCategoryAjaxLoad = ko.observable false
      @newCategoryIsCreating = ko.observable true

      # When making a new enrichment, display only subcategories that fit category
      @newSubcategoryOptions = ko.computed =>
        return ko.utils.arrayFilter @subcategories(), (subcategory) =>
          return subcategory.categoryId() == @newEnrichment.category().id()

      # Subcategory creation fields.
      @newSubcategory =
        name: ko.observable ''
        category: ko.observable ''
      @newSubcategoryNameErrorMessage = ko.observable false
      @newSubcategoryNameSuccessMessage = ko.observable false
      @newSubcategoryNameMessageBody = ko.observable ''
      @newSubcategoryAjaxLoad = ko.observable false
      @newSubcategoryIsCreating = ko.observable true

      # Enrichment creation fields.
      @newEnrichment =
        name: ko.observable ''
        category: ko.observable ''
        subcategory: ko.observable ''
      @newEnrichmentNameErrorMessage = ko.observable false
      @newEnrichmentNameSuccessMessage = ko.observable false
      @newEnrichmentNameMessageBody = ko.observable ''
      @newEnrichmentAjaxLoad = ko.observable false
      @newEnrichmentIsCreating = ko.observable true

      # EnrichmentNote creation fields.
      @newEnrichmentNote = new EnrichmentNote null
      @newEnrichmentNoteError = ko.observable false
      @newEnrichmentNoteSuccess = ko.observable false
      @newEnrichmentNoteAjaxLoad = ko.observable false
      @newEnrichmentNoteIsCreating = ko.observable true

      # Selected enrichment fields
      @currentEnrichment = ko.observable new Enrichment null
      @enrichmentNotes = ko.observableArray []

    # Apply filters
    filterCategory: (category) =>
      if category == @categoryFilter()
        @subcategoryFilter('')
        @categoryFilter('')
      else
        @subcategoryFilter('')
        @categoryFilter(category)
      resizeAllCarousels()

    filterSubcategory: (subcategory) =>
      if subcategory == @subcategoryFilter()
        @subcategoryFilter('')
      else
        @subcategoryFilter(subcategory)
      resizeAllCarousels()
      ## For disable instead of remove, need css rule, not working
      #ko.utils.arrayForEach @enrichments(), (enrichment) ->
      #  if enrichment.subcategoryId() != subcategory.id()
      #    enrichment.disabled = true
      #  else
      #    enrichment.disabled = false

    load: () =>
      # Initialize
      # API limits num results, use &limit=0 (?)
      $.getJSON '/api/v1/category/?format=json', (data) =>
        mappedCategories = $.map data.objects, (item) ->
          return new Category item
        @categories mappedCategories
      $.getJSON '/api/v1/subcategory/?format=json', (data) =>
        mappedSubcategories = $.map data.objects, (item) ->
          return new Subcategory item
        @subcategories mappedSubcategories
      $.getJSON '/api/v1/enrichment/?format=json&limit=0', (data) =>
        mappedEnrichments = $.map data.objects, (item) ->
          return new Enrichment item
        @enrichments mappedEnrichments
        @enrichments.sort (a, b) ->
          if a.name() == b.name()
            return 0
          else if a.name() < b.name()
            return -1
          else
            return 1
        resizeAllCarousels()
      # Get species for enrichmentNote
      $.getJSON '/api/v1/species/?format=json&limit=0', (data) =>
        mappedSpecies = $.map data.objects, (item) ->
          return new Species item
        @species mappedSpecies

    empty: () =>
      @categories null
      @subcategories null
      @enrichments null
      @categoryFilter ''
      @subcategoryFilter ''

    # Modal methods.
    openCreateCategory: () =>
      @newCategory.name ''
      @newCategoryNameErrorMessage false
      @newCategoryNameSuccessMessage false
      @newCategoryNameMessageBody ''
      @newCategoryAjaxLoad false
      @newCategoryIsCreating true

    openCreateSubcategory: () =>
      @newSubcategory.name ''
      @newSubcategory.category ''
      @newSubcategoryNameErrorMessage false
      @newSubcategoryNameSuccessMessage false
      @newSubcategoryNameMessageBody ''
      @newSubcategoryAjaxLoad false
      @newSubcategoryIsCreating true

    openCreateEnrichment: () =>
      @newEnrichment.name ''
      @newEnrichment.subcategory ''
      @newEnrichmentNameErrorMessage false
      @newEnrichmentNameSuccessMessage false
      @newEnrichmentNameMessageBody ''
      @newEnrichmentAjaxLoad false
      @newEnrichmentIsCreating true

    openEnrichmentNote: (current) =>
      @currentEnrichment current
      console.log current.id()
      $.getJSON "/api/v1/enrichmentNote/?format=json&enrichment_id=#{current.id()}", (data) =>
        mappedNotes = $.map data.objects, (item) ->
          return new EnrichmentNote item
        @enrichmentNotes mappedNotes
      $('#modal-enrichment-info').modal('show')
      console.log @currentEnrichment()

    createCategory: () =>
      newCategory =
        name: @newCategory.name()

      # Make sure we are not in the middle of loading.
      if (@newCategoryAjaxLoad())
        console.log "We are already trying to send something"
        return false

      # Validate fields before continuing.
      if (newCategory.name.length == 0)
        @newCategoryNameErrorMessage true
        @newCategoryNameMessageBody 'Category name cannot be blank'
        return

      if (newCategory.name.length > 100)
        @newCategoryNameErrorMessage true
        @newCategoryNameMessageBody 'Category name is too long'
        return

      settings =
        type: 'POST'
        url: '/api/v1/category/?format=json'
        data: JSON.stringify newCategory
        dataType: "json",
        processData:  false,
        contentType: "application/json"

      settings.success = (data, textStatus, jqXHR) =>
        console.log "Category successfully created!"

        # Extract the category id from the Location response header.
        locationsURL = jqXHR.getResponseHeader 'Location'
        pieces = locationsURL.split "/"
        newCategory.id = pieces[pieces.length - 2]

        # Show success message and remove extra weight.
        @newCategoryIsCreating false
        @newCategoryNameSuccessMessage true
        @newCategoryNameErrorMessage false

        console.log newCategory

        # Add new category to @categories and refresh.
        @categories.push {
          name: ko.observable newCategory.name
          id: ko.observable newCategory.id
        }
        resizeAllCarousels()

      settings.error = (jqXHR, textStatus, errorThrown) =>
        console.log "Category not created!"
        @newCategoryNameErrorMessage true
        @newCategoryAjaxLoad false
        @newCategoryNameMessageBody 'An unexpected error occured'

      # Make the ajax call.
      @newCategoryAjaxLoad true
      $.ajax settings

    createSubcategory: () =>
      category = @newSubcategory.category()
      newSubcategory =
        name: @newSubcategory.name()
        category: "/api/v1/category/#{category.id()}/"

      console.log newSubcategory

        # Make sure we are not in the middle of loading.
      if (@newSubcategoryAjaxLoad())
        console.log "We are already trying to send something"
        return

      # Validate fields before continuing.
      if (newSubcategory.name.length == 0)
        @newSubcategoryNameErrorMessage true
        @newSubcategoryNameMessageBody 'Subcategory name cannot be blank'
        return

      if (newSubcategory.name.length > 100)
        @newSubcategoryNameErrorMessage true
        @newSubcategoryNameMessageBody 'Subcategory name is too long'
        return

      settings =
        type: 'POST'
        url: '/api/v1/subcategory/?format=json'
        data: JSON.stringify newSubcategory
        success: @subcategoryCreated
        dataType: "json",
        processData:  false,
        contentType: "application/json"

      settings.success = (data, textStatus, jqXHR) =>
        console.log "Subcategory successfully created!"

        # Extract the category id from the Location response header.
        locationsURL = jqXHR.getResponseHeader 'Location'
        pieces = locationsURL.split "/"
        newSubcategory.id = pieces[pieces.length - 2]

        # Show success message and remove extra weight.
        @newSubcategoryIsCreating false
        @newSubcategoryNameSuccessMessage true
        @newSubcategoryNameErrorMessage false

        # Add new subcategory to @subcategories and refresh.
        @subcategories.push {
          name: ko.observable newSubcategory.name
          id: ko.observable newSubcategory.id
          categoryId: ko.observable category.id()
        }
        resizeAllCarousels()

      settings.error = (jqXHR, textStatus, errorThrown) =>
        console.log "Subcategory not created!"
        @newSubcategoryNameErrorMessage true
        @newSubcategoryAjaxLoad false
        @newSubcategoryNameMessageBody 'An unexpected error occured'

      # Make the ajax call.
      @newSubcategoryAjaxLoad true
      $.ajax settings

    createEnrichment: () =>
        category = @newEnrichment.category()
        subcategory = @newEnrichment.subcategory()
        newEnrichment =
          name: @newEnrichment.name()
          subcategory: "/api/v1/category/#{subcategory.id()}/"

        console.log newEnrichment

          # Make sure we are not in the middle of loading.
        if (@newEnrichmentAjaxLoad())
          console.log "We are already trying to send something"
          return

        # Validate fields before continuing.
        if (newEnrichment.name.length == 0)
          @newEnrichmentNameErrorMessage true
          @newEnrichmentNameMessageBody 'Enrichment name cannot be blank'
          return

        if (newEnrichment.name.length > 100)
          @newEnrichmentNameErrorMessage true
          @newEnrichmentNameMessageBody 'Enrichment name is too long'
          return

        settings =
          type: 'POST'
          url: '/api/v1/enrichment/?format=json'
          data: JSON.stringify newEnrichment
          success: @enrichmentCreated
          dataType: "json",
          processData:  false,
          contentType: "application/json"

        settings.success = (data, textStatus, jqXHR) =>
          console.log "Enrichment successfully created!"

          # Extract the category id from the Location response header.
          locationsURL = jqXHR.getResponseHeader 'Location'
          pieces = locationsURL.split "/"
          newEnrichment.id = pieces[pieces.length - 2]

          # Show success message and remove extra weight.
          @newEnrichmentIsCreating false
          @newEnrichmentNameSuccessMessage true
          @newEnrichmentNameErrorMessage false

          # Add new enrichment to @subcategories and refresh.
          @enrichments.push {
            name: ko.observable newEnrichment.name
            id: ko.observable newEnrichment.id
            subcategoryId: ko.observable subcategory.id()
            ###
            @id = ko.observable data.id
            @name = ko.observable data.name # non-observable is fine
            @categoryId = ko.observable data.subcategory.category.id
            @categoryName = ko.observable data.subcategory.category.name
            @subcategoryId = ko.observable data.subcategory.id
            @subcategoryName = ko.observable data.subcategory.name###
            count: ko.observable 0
            disabled: false
          }
          resizeAllCarousels()

        settings.error = (jqXHR, textStatus, errorThrown) =>
          console.log "Enrichment not created!"
          @newEnrichmentNameErrorMessage true
          @newEnrichmentAjaxLoad false
          @newEnrichmentNameMessageBody 'An unexpected error occured'

        # Make the ajax call.
        @newEnrichmentAjaxLoad true
        $.ajax settings

    createEnrichmentNote: () =>
      newEN = 
        enrichment: "/api/v1/enrichment/#{@currentEnrichment().id()}/"
        instructions: @newEnrichmentNote.instructions()
        limitations: @newEnrichmentNote.limitations()
        species: "/api/v1/species/#{@newEnrichmentNote.species().id()}/"

      console.log newEN

        # Make sure we are not in the middle of loading.
      if (@newEnrichmentNoteAjaxLoad())
        console.log "We are already trying to send something"
        return

      # Validate fields before continuing.
      # TODO

      settings =
        type: 'POST'
        url: '/api/v1/enrichmentNote/?format=json'
        data: JSON.stringify newEN
        success: @enrichmentCreated
        dataType: "json",
        processData:  false,
        contentType: "application/json"

      settings.success = (data, textStatus, jqXHR) =>
        console.log "EnrichmentNote successfully created!"

        # Extract the category id from the Location response header.
        locationsURL = jqXHR.getResponseHeader 'Location'
        pieces = locationsURL.split "/"

        # Push new note to table
        noteToPush =
          enrichment: {id: @currentEnrichment().id()}
          instructions: @newEnrichmentNote.instructions()
          limitations: @newEnrichmentNote.limitations()
          species: {common_name: @newEnrichmentNote.species().commonName()}
          id: pieces[pieces.length - 2]
        console.log noteToPush
        @enrichmentNotes.push new EnrichmentNote noteToPush

        # Show success message and remove extra weight.
        @newEnrichmentNoteIsCreating false
        @newEnrichmentNoteSuccess true
        @newEnrichmentNoteError false

        # Add new enrichment to @subcategories and refresh.

      settings.error = (jqXHR, textStatus, errorThrown) =>
        console.log "Enrichment not created!"
        @newEnrichmentAjaxLoad false
        @newEnrichmentNameError 'An unexpected error occured'

      # Make the ajax call.
      @newEnrichmentAjaxLoad true
      $.ajax settings

  class ObservationListViewModel
    constructor: () ->
      # Arrays for holding data
      @observations = ko.observableArray []
      @behaviorType = [
        { id: 0, type: 'N/A'}
        { id: 1, type: 'Positive'}
        { id: -1, type: 'Negative'}
        { id: -2, type: 'Avoid'}
      ]
      @activeObservation = ko.observable null
      @activeAnimalObservation = ko.observable null
      @activeBehaviors = ko.observableArray []

      @newBehaviorType = ko.observable null
      @newBehaviorDesc = ko.observable null

      @selectedBehavior = ko.observable null

      updateAnimalObservation.subscribe (data) =>
          console.log "saving animal observation"
          @saveAnimalObservation data
        , @, "saveAnimalObservation"


    loadBehaviors: (observation, animalObservation) =>
      @activeObservation observation
      @activeAnimalObservation animalObservation
      console.log "getting behaviors for #{observation.enrichment().id}"
      $.getJSON "/api/v1/behavior/?format=json&enrichment_id=#{observation.enrichment().id}", (data) =>
        console.log data
        @activeBehaviors data.objects
        console.log @activeBehaviors()

    addNewBehavior: (data) =>
      behavior = {}
      behavior.description = @newBehaviorDesc()
      behavior.reaction = @newBehaviorType()
      behavior.enrichment = @activeObservation().enrichment().resource_uri
      console.log behavior
      $.ajax "/api/v1/behavior/?format=json", {
        data: JSON.stringify behavior
        dataType: "json"
        type: "POST"
        contentType: "application/json"
        processData: false
        success: (result) =>
          console.log result
          console.log "Created behavior"
          @activeBehaviors.push result
          @newBehaviorType null
          @newBehaviorDesc null
        error: (result) =>
          console.log result
      }
    saveBehavior: () =>
      try
        console.log "saving behavior #{@selectedBehavior().id} for #{@activeAnimalObservation().id}"
      catch TypeError
        return
      console.log @selectedBehavior()
      obs = {}
      obs.behavior = @selectedBehavior().resource_uri
      console.log obs
      $.ajax "/api/v1/animalObservation/#{@activeAnimalObservation().id}/?format=json", {
        data: JSON. stringify obs
        dataType: "json"
        type: "PATCH"
        contentType: "application/json"
        processData: false
        success: (result) =>
          console.log "finished saving behavior"
          console.log result
          @activeObservation null
          @activeBehaviors []
          @activeAnimalObservation null
          @selectedBehavior null
        error: (result) =>
          console.log result
      }


    finishObservation: () =>
      try
        console.log "finishing observation: "+@activeObservation().id
      catch TypeError
        return
      obs = {}
      obs.date_finished = new Date().toISOString().split('.')[0]
      console.log obs
      $.ajax "/api/v1/observation/#{@activeObservation().id}/?format=json", {
        data: JSON.stringify obs
        dataType: "json"
        type: "PATCH"
        contentType: "application/json"
        processData: false
        success: (result) => 
          console.log "finished observation"
          @observations.remove @activeObservation()
          @activeObservation null
        error: (result) =>
          console.log result
      }

    load: () =>
      # Get data from API
      $.getJSON '/api/v1/observation/?format=json&staff_id='+window.userId, (data) =>
        mapped = $.map data.objects, (item) ->
          return new Observation item
        @observations mapped
        # TODO can remove below
        @observations.subscribe (value) ->
          console.log(value)
          console.log "observation change"

    saveAnimalObservation: (data) =>
      console.log "here"
      obs = {}
      obs[data.type] = data.value
      console.log JSON.stringify obs
      $.ajax "/api/v1/animalObservation/#{data.id}/?format=json", {
        data: JSON.stringify obs
        dataType: "json"
        type: "PATCH"
        contentType: "application/json"
        processData: false
        success: (result) => 
          console.log result
        error: (result) =>
          console.log result
      }
      return

    empty: () =>  
      @observations []

    prettyDate: (date) =>
      d = new Date Date.parse date
      return d.toString()


  class StaffListViewModel
    constructor: () ->
      # Array for staff data
      @staff = ko.observableArray []
      @currentStaff = ko.observable
        full_name: ''
        animal_title: ''
        housingGroups: []
        loading: false
        id: ''
      @exhibits = ko.observable null
      @housingGroups = ko.observable null

      # New staff modal stuff
      @newStaff =
        firstName: ko.observable ''
        lastName: ko.observable ''
        password1: ko.observable ''
        password2: ko.observable ''
        isSuperuser: ko.observable false
      @newStaffError = ko.observable null
      @newStaffWarning = ko.observable null
      @newStaffSuccess = ko.observable false
      @newStaffIsCreating = ko.observable true
      @newStaffAjaxLoad = ko.observable false

      # Bulk upload fields.
      # The @bulkStaff field is in two different ways in the HTML View.  First,
      # it is used for previewing the upload lines.  After a successful POST is
      # sent off and returned, an array of objects is also returned.  The
      # @bulkStaff field will then be used to populate the second of two tables
      # and it will contain actual Staff models, as opposed to the temporary
      # one created in @fileChanged.
      @bulkStaff = ko.observableArray []
      @bulkError = ko.observable null
      @bulkWarning = ko.observable null
      @bulkSuccess = ko.observable null
      @bulkAjaxInProgress = ko.observable false

      # Add HG to staff modal
      @newHousingGroup =
        exhibit: ko.observable null
        housingGroup: ko.observable null
      @newHousingGroupError = ko.observable null
      @newHousingGroupWarning = ko.observable null
      @newHousingGroupSuccess = ko.observable false
      @newHousingGroupIsCreating = ko.observable true
      @newHousingGroupAjaxLoad = ko.observable false

      @newHousingGroupOptions = ko.computed =>
        if @newHousingGroup.exhibit()?
          return @newHousingGroup.exhibit().housingGroups()
        else
          return []

      @newHousingGroupAnimals = ko.computed =>
        if @newHousingGroup.housingGroup()?
          return @newHousingGroup.housingGroup().animals()
        else
          return []

    openStaffCreate: () ->
      @newStaff.firstName ''
      @newStaff.lastName ''
      @newStaff.password1 ''
      @newStaff.password2 ''
      @newStaff.isSuperuser false
      @newStaffError null
      @newStaffWarning null
      @newStaffSuccess false
      @newStaffIsCreating true
      @newStaffAjaxLoad false

    openBulkCreate: () ->
      $('input[type="file"]').val('')
      @bulkStaff []
      @bulkError null
      @bulkWarning null
      @bulkSuccess null
      @bulkAjaxInProgress false

    fileChanged: (viewModel, event) =>
      # Extract file from event, create FileReader, and empty current staff.
      file = event.target.files[0]
      reader = new FileReader()
      @bulkStaff []
      @bulkWarning null
      @bulkError null

      # Set file traversal function.
      reader.onload = (ev) =>
        lines = ev.target.result.split /[\n|\r]/
        anyLinesIncluded = false

        for line, index in lines
          # Create a staff object and add it to bulkStaff array.
          index = index + 1
          staffObj =
            line: line
            lineNumber: ko.observable index
            firstName: ko.observable ''
            lastName: ko.observable ''
            password: ko.observable ''
            isSuperuser: ko.observable 'No'
            validLine: ko.observable false
            includeLine: ko.observable false
          @bulkStaff.push staffObj
          fields = line.split ','

          # Perform some error checking.
          if (line == "")
            if (index != lines.length)
              @bulkWarning "Line #{index}: Line is empty"
            continue
          if (fields.length != 4)
            @bulkWarning "Line #{index}: Invalid amount of lines"
            continue
          if (fields[0] == "")
            @bulkWarning "Line #{index}: First name is empty"
            continue
          if (fields[1] == "")
            @bulkWarning "Line #{index}: Last name is empty"
            continue
          if (fields[2] == "")
            @bulkWarning "Line #{index}: Password is empty"
            continue

          # Finally, modify object to assign values.
          staffObj.firstName fields[0]
          staffObj.lastName fields[1]
          staffObj.password fields[2]
          if (fields[3] == "1")
            staffObj.isSuperuser 'Yes'
          staffObj.includeLine true
          staffObj.validLine true
          anyLinesIncluded = true

        if (not anyLinesIncluded)
          @bulkWarning null
          @bulkError 'This file contains no valid lines'
          @bulkStaff []

      # Initiate reading.
      reader.readAsText file

    # bulkCreateStaff
    bulkCreateStaff: () =>
      uploadStaff = []

      for staff in @bulkStaff()
        if (staff.validLine() and staff.includeLine())
          uploadStaff.push staff.line

      console.log uploadStaff

      settings =
        type: 'POST'
        url: '/api/v1/user/bulk/?format=json&always_return_data=true'
        data: JSON.stringify uploadStaff
        dataType: "json",
        processData:  false,
        contentType: "application/json"

      settings.success = (data, textStatus, jqXHR) =>
        console.log "Batch staff created"
        console.log data
        console.log textStatus

        @bulkStaff []
        @bulkSuccess 'Staff successfully uploaded!'
        @bulkWarning null
        @bulkError null

        # Insert all into staff array.
        for newData in data.objects
          staffTemp =
            user: newData
            id: newData.id
          staff = new Staff staffTemp
          console.log staff
          @staff.push staff
          @bulkStaff.push staff

      settings.error = (jqXHR, textStatus, errorThrown) =>
        console.log "Batch staff error"
        @bulkWarning null
        @bulkError 'An unexpected error occured'

      # Make the ajax call.
      @bulkAjaxInProgress true
      $.ajax settings

    createStaff: () ->
      newStaff =
        first_name: @newStaff.firstName()
        last_name: @newStaff.lastName()
        is_superuser: @newStaff.isSuperuser()
        password: @newStaff.password1()

      # Perform error checking first.
      if (newStaff.first_name == '')
        @newStaffError 'First name cannot be empty'
        return
      if (newStaff.last_name == '')
        @newStaffError 'Last name cannot be empty'
        return
      if (newStaff.password != @newStaff.password2())
        @newStaffError 'Passwords do not match'
        return
      if (newStaff.password.length < 4)
        @newStaffError 'Password must be at least 4 characters'
        return

      # Create ajax settings.
      settings =
        type: 'POST'
        url: '/api/v1/user/add_user/?format=json&always_return_data=true'
        data: JSON.stringify newStaff
        dataType: "json",
        processData:  false,
        contentType: "application/json"

      settings.success = (data, textStatus, jqXHR) =>
        console.log "Staff successfully created!"
        staff =
          user: data.object
          id: data.object.id

        # Create a staff members and insert.
        @staff.push new Staff staff
        resizeAllCarousels()

        # Show success message and remove extra weight.
        @newStaffIsCreating false
        @newStaffSuccess "#{staff.user.first_name} #{staff.user.last_name} " +
            "has been created with the username #{staff.user.username}"
        @newStaffError false

      settings.error = (jqXHR, textStatus, errorThrown) =>
        console.log "Staff not created!"
        @newStaffAjaxLoad false
        @newStaffError 'An unexpected error occured'

      # Make AJAX call.
      @newStaffAjaxLoad true
      $.ajax settings

    addHousingGroup: () =>
      try
        console.log ("adding HG " + @newHousingGroup.housingGroup().name())
      catch TypeError
        return
      data = {}
      data.housing_group = ['/api/v1/housingGroup/' + @newHousingGroup.housingGroup().id() + '/']
      $.each @currentStaff().housingGroups(), (index, value) =>
        hg = if $.isFunction(value) then value() else value
        if data.housing_group.indexOf('api/v1/housingGroup/' + hg.id() + '/') == -1
          data.housing_group.push '/api/v1/housingGroup/' + hg.id() + '/'
      console.log JSON.stringify data
      $.ajax "/api/v1/staff/#{@currentStaff().id()}/?format=json", {
        data: JSON.stringify data
        dataType: "json"
        type: "PUT"
        contentType: "application/json"
        processData: false
        success: (result, status) => 
          console.log "added HG?!"
          console.log status
          newHG = new HousingGroup null
          target = @newHousingGroup.housingGroup
          newHG.id target().id()
          newHG.name target().name()
          newHG.staff target().staff()
          newHG.resourceURI = target().resourceURI
          newHG.animals target().animals()

          @currentStaff().housingGroups.push newHG
        error: (result) =>
          console.log result
      }

    deleteHousingGroup: (hg) =>
      idToDelete = hg.id()
      url = "/api/v1/staff/#{@currentStaff().id()}/?format=json"

      # Have only the proper list of housingGroups after deletion
      updatedGroupList = []
      $.each @currentStaff().housingGroups(), (index, value) ->
        hgUrl = "/api/v1/housingGroup/#{value.id()}/"
        updatedGroupList.push hgUrl if value.id() != idToDelete

      # Prepare data to be sent
      data = {'housing_group': updatedGroupList}
      $.ajax url, {
        data: JSON.stringify data
        dataType: "json"
        type: "PUT"
        contentType: "application/json"
        processData: false
        success: (result) =>
          console.log "removed HG"
          @currentStaff().housingGroups.remove hg
        error: (result) =>
          console.log result
      }

    viewInfo: (staff) =>
      staff.loadInfo()
      $('#modal-staff-info').modal('show')
      @currentStaff staff

    load: () ->
      # Get data from API
      $.getJSON '/api/v1/staff/?format=json', (data) =>
        mapped = $.map data.objects, (item) ->
          return new Staff item
        @staff mapped
      $.getJSON '/api/v1/exhibit/?format=json', (data) =>
        mapped = $.map data.objects, (item) ->
          return new Exhibit item
        @exhibits mapped

  # The big momma
  PawsViewModel = 
    AnimalListVM: new AnimalListViewModel()
    EnrichmentListVM: new EnrichmentListViewModel()
    ObservationListVM: new ObservationListViewModel()
    StaffListVM: new StaffListViewModel()
  ko.applyBindings PawsViewModel.AnimalListVM, document.getElementById 'animalListContainer'
  ko.applyBindings PawsViewModel.EnrichmentListVM, document.getElementById 'enrichmentListContainer'
  ko.applyBindings PawsViewModel.ObservationListVM, document.getElementById 'observationsContainer'
  ko.applyBindings PawsViewModel.StaffListVM, document.getElementById 'staffContainer'


  # Sammy
  # ################
  window.sammy = Sammy (context) =>
    context.get '/', () => # use regex?
      $('#main > div:not(#home)').hide()
      PawsViewModel.EnrichmentListVM.empty()
      PawsViewModel.AnimalListVM.empty()
      $('#home').show()
      resizeAllCarousels()
    context.get '/animals', () =>
      $('#main > div:not(#animalListContainer)').hide()
      PawsViewModel.EnrichmentListVM.empty()
      PawsViewModel.AnimalListVM.load()
      $('#animalListContainer').show()
      resizeAllCarousels()
    context.get '/enrichments', () =>
      $('#main > div:not(#enrichmentListContainer)').hide()
      PawsViewModel.AnimalListVM.empty()
      PawsViewModel.EnrichmentListVM.load()
      $('#enrichmentListContainer').show()
      resizeAllCarousels()
    context.get '/observe', () =>
      $('#main > div:not(#observationsContainer)').hide()
      PawsViewModel.AnimalListVM.empty()
      PawsViewModel.EnrichmentListVM.empty()
      PawsViewModel.ObservationListVM.load()
      $('#observationsContainer').show()
      resizeAllCarousels()

    context.get '/staff', () =>
      $('#main > div:not(#staffContainer)').hide()
      PawsViewModel.AnimalListVM.empty()
      PawsViewModel.EnrichmentListVM.empty()
      PawsViewModel.ObservationListVM.empty()
      PawsViewModel.StaffListVM.load()
      $('#staffContainer').show()
    context.get '/auth/logout', () =>
      window.location = '/auth/logout' 
  sammy.run()

  ###
  console.log PawsViewModel.ObservationListVM.observations
  console.log PawsViewModel.ObservationListVM.observations()
  $.each PawsViewModel.ObservationListVM.observations(), (obs) ->
    console.log "in"
    console.log obs
    obs.animal_observations.indirectUse.subscribe (value) ->
      console.log this
      console.log value 
      console.log "observation array changed"
      ###
  # UI
  # ################
  
  MAX_SCROLLER_ROWS = 3
  window.scrollers = {}

  resizeCarousel = (scroller, numRows=1, fixedWidth=true) ->
    oldWidth = $(scroller).width()
    length = $(scroller).find('ul li').length
    newWidth = 0;
    # Fixed width items, don't compute width of every li
    if fixedWidth
      console.log "fixed"
      singleWidth = $(scroller).find('ul li:first').outerWidth(true)
      newWidth = Math.ceil(length / numRows) * singleWidth
      while newWidth > 8000
        numRows++
        newWidth = Math.ceil(length / numRows) * singleWidth
    # Not fixed width, compute the width of every li dynamically
    else
      $(scroller).find('ul li').each ->
        newWidth += $(this).outerWidth(true)
      newWidth /= numRows
      newWidth = 8000 if newWidth > 8000
      console.log newWidth
    if newWidth != oldWidth
      console.log 'Resizing carousel from ' + oldWidth + ' to ' + newWidth + ' with ' + numRows + ' rows'
      $(scroller).width newWidth
      return true
    return false

  resizeAllCarousels = (refresh=true) ->
    $('.carousel-scroller').each ->
      if $(this).hasClass 'carousel-rows'
        numRows = Math.min Math.floor(($(window).height()-$(this).parent().offset().top)/$(this).find('li:first').outerHeight(true)), MAX_SCROLLER_ROWS
        console.log "numrows: #{numRows}"
      else
        numRows = 1
      resized = resizeCarousel this, numRows, $(this).hasClass 'carousel-fixed-width'
      if refresh and resized
        console.log 'Refreshing carousel'
        $.each scrollers, (key, value) ->
          value.refresh()
    $('.list-vertical').each ->
      $.each scrollers, (key, value) ->
        value.refresh()


  scrollers.categorySelector = new iScroll 'categorySelector', {
    vScroll: false
    momentum: true
    bounce: true
    hScrollbar: false
  }
  scrollers.subcategorySelector = new iScroll 'subcategorySelector', {
    vScroll: false
    momentum: true
    bounce: true
    hScrollbar: false
  }
  scrollers.enrichmentSelector = new iScroll 'enrichmentSelector', {
    vScroll: false
    momentum: true
    bounce: true
    hScrollbar: false
  }
  scrollers.observationEnrichments = new iScroll 'observationEnrichments', {
    vScroll: true
    hScroll: false
    momentum: true
    bounce: true
    vScrollbar: true
  }
  $(window).resize ->
    clearTimeout window.resizeTimeout
    window.resizeTimeout = setTimeout resizeAllCarousels, 500

  $('#animal-modal').modal({
    show: false
  })

  # Enable dismissal of an alert via javascript:
  $(".alert").alert()


