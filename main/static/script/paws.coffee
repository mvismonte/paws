$(document).ready ->


  # Knockout
  # ###############


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
        @animal = ko.observable new Animal data.animal
        @observationId = ko.observable data.observation.id
        @interactionTime = ko.observable data.interaction_time
        @behavior = ko.observable data.behavior
        @description = ko.observable data.description
        @indirectUse = ko.observable data.indirectUse
      else
        @animal = ko.observable null
        @observationId = ko.observable null
        @interactionTime = ko.observable null
        @behavior = ko.observable null
        @description = ko.observable null
        @indirectUse = ko.observable null

  class Exhibit
    constructor: (data) ->
      @code = ko.observable data.code
      @housingGroups = ko.observableArray $.map data.housing_groups, (item) ->
        return new HousingGroup item
      @fullName = ko.computed =>
        return 'Exhibit ' + @code()

  class HousingGroup
    constructor: (data) ->
      @name = ko.observable data.name
      @staff = ko.observable data.staff
      @animals = ko.observableArray $.map data.animals, (item) ->
        return new Animal item

  class Category
    constructor: (data={}) ->
      @name = ko.observable data.name
      @id = ko.observable data.id

  class Enrichment
    constructor: (data) ->
      @id = ko.observable data.id
      @name = ko.observable data.name # non-observable is fine
      @categoryId = ko.observable data.subcategory.category.id
      @categoryName = ko.observable data.subcategory.category.name
      @subcategoryId = ko.observable data.subcategory.id
      @subcategoryName = ko.observable data.subcategory.name
      @count = ko.observable 0
      @disabled = false

  class EnrichmentNote
    constructor: (data) ->
      @enrichmentId = ko.observable data.enrichment.id
      @speciesCommonName = ko.observable data.species.common_name
      @speciesId = ko.observable data.species.id
      @speciesScientificName = ko.observable data.species.scientific_name
      @limitations = ko.observable data.limitations
      @instructions = ko.observable data.instructions

  class Observation
    constructor: (data=null) ->
      if data?
        @enrichment = ko.observable data.enrichment # not using .name for now
        @animal_observations = ko.observable data.animal_observations # not using camel case to reflect JSON
        @dateCreated = ko.observable data.date_created
        @dateFinished = ko.observable data.date_finished
      else
        @enrichment = ko.observable null
        @animal_observations = ko.observableArray []
        @behavior = ko.observable null
        @dateCreated = ko.observable null
    modalTitle: () ->
      length = @animal_observations().length
      pluralized = if length > 1 then ' animals' else ' animal'
      return 'Observing ' + length + pluralized

  class Staff
    constructor: (data) ->
      console.log data
      @id = ko.observable data.id
      @first_name = ko.observable data.user.first_name
      @last_name = ko.observable data.user.last_name
      @username = ko.observable data.user.username

  class Species
    constructor: (data) ->
      @commonName = ko.observable data.common_name
      @scientificName = ko.observable data.scientific_name
      @id = ko.observable data.id

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
      @exhibits = ko.observableArray []
      @categories = ko.observableArray []
      @subcategories = ko.observableArray []
      @enrichments = ko.observableArray []
      @enrichmentNotes = ko.observableArray []

      # Current filter variables
      @currentSpecies = ko.observable ''
      @currentEnrichment = ko.observable null

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
      @modalTitleAnimals = ko.computed =>
        length = @selectedAnimals().length
        pluralized = if length != 1 then ' animals' else ' animal'
        enrichName = if @currentEnrichment()? then @currentEnrichment().name() + ' - ' else ''
        return enrichName + 'Observing ' + length + pluralized

      # Observation stuff
      @observation = ko.observable new Observation()

      # Filtered lists

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
      else
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
      $.getJSON '/api/v1/exhibit/?format=json', (data) =>
        mappedExhibits = $.map data.objects, (item) ->
          return new Exhibit item
        @exhibits mappedExhibits

    # Check if ID exists in observableArray
    idInArray: (id, array) =>
      retval = false
      $.each array, (index, value) =>
        if id == value.id()
          retval = true
          return false # break
      return retval

    gotoStep2: () =>
      if @currentEnrichment()?
        $('#modal-observe-1').modal('hide')
        $('#modal-observe-2').modal('show')

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
      @newCategory = new Category
      @newCategory.name ''
      delete @newCategory.id

      @newSubcategory = new Subcategory
      @newSubcategory.name ''
      @newSubcategory.categoryId ''
      delete @newSubcategory.id

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

    empty: () =>
      @categories null
      @subcategories null
      @enrichments null
      @categoryFilter ''
      @subcategoryFilter ''

    # Modal methods.
    createCategory: () =>
      alert @newCategory.name()
      newCategory =
        name: @newCategory.name()

      settings =
        type: 'POST'
        url: '/api/v1/category/?format=json'
        data: JSON.stringify newCategory
        success: @categoryCreated
        dataType: "application/json",
        processData:  false,
        contentType: "application/json"

      $.ajax settings

    categoryCreated: (data, textStatus, jqXHR) =>
      alert "Category successfully created!"
      console.log data
      console.log textStatus
      console.log jqXHR

      # Need to add logic to append newly created category to the list.

    createSubcategory: () =>
      category = @newSubcategory.categoryId()
      console.log category
      newSubcategory =
        name: @newSubcategory.name()
        category: "/api/v1/category/#{category.id()}/"

      console.log newSubcategory

      settings =
        type: 'POST'
        url: '/api/v1/subcategory/?format=json'
        data: JSON.stringify newSubcategory
        success: @subcategoryCreated
        dataType: "application/json",
        processData:  false,
        contentType: "application/json"

      $.ajax settings

    subcategoryCreated: (data, textStatus, jqXHR) =>
      alert "Subcategory successfully created!"
      console.log data
  
  class ObservationListViewModel
    constructor: () ->
      # Arrays for holding data
      @observations = ko.observableArray []
      @behaviorType = [
        { id: -2, type: 'Avoid'}
        { id: -1, type: 'Negative'}
        { id: 0, type: 'N/A'}
        { id: 1, type: 'Positive'}
      ]
      @activeObservation = ko.observable null

    finishObservation: () =>
      console.log "finishing observation "+@activeObservation().id
      return
      $.ajax "/api/v1/observation/"+@activeObservation().id+"/?format=json", {
          data: ko.toJSON { objects: self.activeObservation }
          type: "PATCH"
          contentType: "application/json"
          success: (result) -> 
            alert(result)
      }

    load: () =>
      # Get data from API
      $.getJSON '/api/v1/observation/?format=json', (data) =>
        #mapped = $.map data.objects, (item) ->
        #  return new Observation item
        @observations data.objects

    empty: () =>
      @observations null

  class StaffListViewModel
    constructor: () ->
      # Array for staff data
      @staff = ko.observableArray []

    load: () ->
      # Get data from API
      $.getJSON '/api/v1/staff/?format=json&staff_id='+'', (data) =>
        console.log data
        mapped = $.map data.objects, (item) ->
          return new Staff item
        @staff mapped

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

  PawsViewModel.ObservationListVM.observations.subscribe (value) ->
    console.log this
    console.log value
    console.log "hi"


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
      newWidth = Math.ceil(length / numRows)*$(scroller).find('ul li:first').outerWidth(true) + 10
    # Not fixed width, compute the width of every li dynamically
    else
      $(scroller).find('ul li').each ->
        newWidth += $(this).outerWidth(true)
    newWidth /= numRows if length/numRows > 1
    if newWidth != oldWidth
      console.log 'Resizing carousel from ' + oldWidth + ' to ' + newWidth + ' with ' + numRows + ' rows'
      $(scroller).width newWidth
      return true
    return false

  resizeAllCarousels = (refresh=true) ->
    $('.carousel-scroller').each ->
      if $(this).hasClass 'carousel-rows'
        numRows = Math.min Math.floor(($(window).height()-$(this).parent().offset().top)/$(this).find('li:first').outerHeight(true)), MAX_SCROLLER_ROWS
        resized = resizeCarousel this, numRows, false
      else
        resized = resizeCarousel this, 1, false
      if refresh and resized
        console.log 'Refreshing carousel'
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
