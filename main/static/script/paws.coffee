$(document).ready ->


  # Knockout
  # ###############


  # Models
  # ----------------
  class Animal
    constructor: (data) ->
      @name = ko.observable data.name
      @id = ko.observable parseInt(data.id)
      @speciesCommonName = ko.observable data.species.common_name
      @speciesId = ko.observable data.species.id
      @speciesScientificName = ko.observable data.species.scientific_name
      @active = ko.observable false
    toggleActive: () ->
      @active !@active()

  class AnimalObservation
    constructor: (data=null) ->
      @animalId = ko.observable null
      @observationId = ko.observable null
      @interactionTime = ko.observable null
      @behavior = ko.observable null
      @description = ko.observable null
      @indirectUse = ko.observable null
      if data != null
        @animalId data.animal.id
        @observationId data.observation.id
        @interactionTime data.interaction_time
        @behavior data.behavior
        @description data.description
        @indirectUse data.indirectUse

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
      @name = ko.observable data.name # non-observable is fine
      @categoryId = ko.observable data.subcategory.category.id
      @categoryName = ko.observable data.subcategory.category.name
      @subcategoryId = ko.observable data.subcategory.id
      @subcategoryName = ko.observable data.subcategory.name
      @disabled = false

  class Observation
    constructor: (data=null) ->
      @enrichment = ko.observable null
      @animalObservations = ko.observableArray []
      @behavior = ko.observable null
      if data != null
        @enrichment data.enrichment.name
        @animalObservations data.animal_observations
        @behavior data.behavior
    modalTitle: () ->
      length = @animalObservations().length
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
      if (data?)
        @name = ko.observable data.name
        @id = ko.observable data.id
        @categoryId = ko.observable data.category.id
      else
        @name = ko.observable ''
        @id = ko.observable ''
        @categoryId = ko.observable ''

  # ViewModels
  # ----------------
  class AnimalListViewModel
    constructor: () ->
      # Arrays for holding data
      @species = ko.observableArray []
      @animals = ko.observableArray []
      @exhibits = ko.observableArray []

      # Current filter variables
      @currentSpecies = ko.observable ''

      # Compute the filtered lists
      @filterAnimalsBySpecies = ko.computed =>
        species = @currentSpecies()
        if species == ''
          return @animals()
        return ko.utils.arrayFilter @animals(), (animal) ->
          return animal.speciesId() == species.id()

      # Enrichment application
      # Current animal selection(s)
      @selectedAnimals = ko.observableArray []

      # Observation stuff
      @observation = ko.observable new Observation()

    # Apply filters
    setCurrentSpecies: (species) =>
      if species == @currentSpecies()
        @currentSpecies('')
      else
        @currentSpecies(species)
      resizeAllCarousels()

    # Select a single animal
    selectAnimal: (animal) =>
      if @selectedAnimals.indexOf(animal.id()) == -1
        @selectedAnimals.push animal.id()
      else
        @selectedAnimals.remove animal.id()
      #console.log @selectedAnimals()

    # Select animal(s) functions
    selectExhibit: (exhibit) =>
      selectAnimals = []
      deselectAnimals = []
      $.each exhibit.housingGroups(), (i, hg) =>
        $.each hg.animals(), (index, animal) =>
          if @selectedAnimals.indexOf(animal.id()) == -1
            selectAnimals.push animal.id()
          else
            deselectAnimals.push animal.id()
      if selectAnimals.length > 0
        $.each selectAnimals, (index, animal) =>
          @selectedAnimals.push animal
      else
        $.each deselectAnimals, (index, animal) =>
          @selectedAnimals.remove animal
      #console.log @selectedAnimals()

    newObservation: () =>
      @observation().animalObservations $.map @selectedAnimals(), (item) ->
        animalOb = new AnimalObservation()
        animalOb.animalId item
        return animalOb
      console.log @observation().animalObservations()

    load: () =>
      # Get data from API
      # $.getJSON '/api/v1/species/?format=json', (data) =>
      #   mappedSpecies = $.map data.objects, (item) ->
      #     return new Species item
      #   @species mappedSpecies

      # $.getJSON '/api/v1/animal/?format=json', (data) =>
      #   mappedAnimals = $.map data.objects, (item) ->
      #     return new Animal item
      #   @animals mappedAnimals
      #   resizeAllCarousels(false)

      $.getJSON '/api/v1/exhibit/?format=json', (data) =>
        mappedExhibits = $.map data.objects, (item) ->
          return new Exhibit item
        @exhibits mappedExhibits

    empty: () =>
      @species null
      @animals null
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

    save: () =>
      $.ajax "/api/v1/observation/", {
          data: ko.toJSON { objects: self.observations }
          type: "PUT"
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
      $.getJSON '/api/v1/staff/?format=json', (data) =>
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

  # Sammy
  # ################
  window.sammy = Sammy (context) =>
    context.get '/', () => # use regex?
      $('#main > div').hide()
      PawsViewModel.EnrichmentListVM.empty()
      PawsViewModel.AnimalListVM.empty()
      $('#home').show()
      resizeAllCarousels()
    context.get '/animals', () =>
      $('#main > div').hide()
      PawsViewModel.EnrichmentListVM.empty()
      PawsViewModel.AnimalListVM.load()
      $('#animalListContainer').show()
      resizeAllCarousels()
    context.get '/enrichments', () =>
      $('#main > div').hide()
      PawsViewModel.AnimalListVM.empty()
      PawsViewModel.EnrichmentListVM.load()
      $('#enrichmentListContainer').show()
      resizeAllCarousels()
    context.get '/observe', () =>
      $('#main > div').hide()
      PawsViewModel.AnimalListVM.empty()
      PawsViewModel.EnrichmentListVM.empty()
      PawsViewModel.ObservationListVM.load()
      $('#observationsContainer').show()
      resizeAllCarousels()
    context.get '/staff', () =>
      $('#main > div').hide()
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
        scrollers[$(this).parent().prop('id')].refresh()

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
  scrollers.speciesSelector = new iScroll 'speciesSelector', {
    vScroll: false
    momentum: true
    bounce: true
    hScrollbar: false
  }
  scrollers.animalSelector = new iScroll 'animalSelector', {
    vScroll: false
    momentum: true
    bounce: true
    hScrollbar: false
  }


  $(window).resize ->
    clearTimeout window.resizeTimeout
    window.resizeTimeout = setTimeout resizeAllCarousels, 500

  $('#animal-modal').modal({
    show: false
  })
