$(document).ready ->


  # Knockout
  # ###############


  # Models
  # ----------------
  class Animal
    constructor: (data) ->
      @name = ko.observable data.name
      @speciesCommonName = ko.observable data.species.common_name
      @speciesId = ko.observable data.species.id
      @speciesScientificName = ko.observable data.species.scientific_name

      @active = ko.observable false
    toggleActive: () ->
      @active !@active()

  class Category
    constructor: (data) ->
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
    constructor: (data) ->
      @enrichment = ko.observable data.enrichment.name
      @animalObservations = ko.observableArray data.animal_observations
      @behavior = ko.observable data.behavior

  class Species
    constructor: (data) ->
      @commonName = ko.observable data.common_name
      @scientificName = ko.observable data.scientific_name
      @id = ko.observable data.id

  class Subcategory
    constructor: (data) ->
      @name = ko.observable data.name
      @id = ko.observable data.id
      @categoryId = ko.observable data.category.id

  # ViewModels
  # ----------------
  class AnimalListViewModel
    constructor: () ->
      # Arrays for holding data
      @species = ko.observableArray []
      @animals = ko.observableArray []

      # Current filter variables
      @currentSpecies = ko.observable ''

      # Apply filters
      @setCurrentSpecies = (species) =>
        if species == @currentSpecies()
          @currentSpecies('')
        else
          @currentSpecies(species)
        resizeAllCarousels()

      # Compute the filtered lists
      @filterAnimalsBySpecies = ko.computed =>
        species = @currentSpecies()
        if species == ''
          return @animals()
        return ko.utils.arrayFilter @animals(), (animal) ->
          return animal.speciesId() == species.id()

      @load = () =>
        # Get data from API
        $.getJSON '/api/v1/species/?format=json', (data) =>
          mappedSpecies = $.map data.objects, (item) ->
            return new Species item
          @species mappedSpecies

        $.getJSON '/api/v1/animal/?format=json', (data) =>
          mappedAnimals = $.map data.objects, (item) ->
            return new Animal item
          @animals mappedAnimals
          resizeAllCarousels(false)
      @empty = () =>
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

      # Apply filters
      @filterCategory = (category) =>
        if category == @categoryFilter()
          @subcategoryFilter('')
          @categoryFilter('')
        else
          @subcategoryFilter('')
          @categoryFilter(category)
        resizeAllCarousels()

      @filterSubcategory = (subcategory) =>
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


      @load = () =>
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
      @empty = () =>
        @categories null
        @subcategories null
        @enrichments null
        @categoryFilter ''
        @subcategoryFilter ''

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

      @save = () =>
        $.ajax "/api/v1/observation/", {
            data: ko.toJSON { objects: self.observations }
            type: "PUT"
            contentType: "application/json"
            success: (result) -> 
              alert(result)
        }

      @load = () =>
        # Get data from API
        $.getJSON '/api/v1/observation/?format=json', (data) =>
          mapped = $.map data.objects, (item) ->
            return new Observation item
          @observations data.objects

      @empty = () =>
        @observations null

  # The big momma
  PawsViewModel = 
    AnimalListVM: new AnimalListViewModel()
    EnrichmentListVM: new EnrichmentListViewModel()
    ObservationListVM: new ObservationListViewModel()
  ko.applyBindings PawsViewModel.AnimalListVM, document.getElementById 'animalListContainer'
  ko.applyBindings PawsViewModel.EnrichmentListVM, document.getElementById 'enrichmentListContainer'
  ko.applyBindings PawsViewModel.ObservationListVM, document.getElementById 'observationsContainer'

  # Sammy
  # ################
  Sammy (context) =>
    context.get '/', () =>
      PawsViewModel.EnrichmentListVM.empty()
      PawsViewModel.AnimalListVM.empty()
      $('#home').show()
      resizeAllCarousels()
    context.get '/animals', () =>
      $('#home').hide()
      PawsViewModel.EnrichmentListVM.empty()
      PawsViewModel.AnimalListVM.load()
      resizeAllCarousels()
    context.get '/enrichments', () =>
      $('#home').hide()
      PawsViewModel.AnimalListVM.empty()
      PawsViewModel.EnrichmentListVM.load()
      resizeAllCarousels()
    context.get '/#observe', () =>
      $('#home').hide()
      PawsViewModel.AnimalListVM.empty()
      PawsViewModel.EnrichmentListVM.empty()
      PawsViewModel.ObservationListVM.load()
      resizeAllCarousels()
  .run()


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
