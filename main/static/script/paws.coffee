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

  # The big momma
  PawsViewModel = 
    AnimalListVM: new AnimalListViewModel()
  ko.applyBindings PawsViewModel.AnimalListVM

  # Sammy
  # ################
  Sammy (context) =>
    context.get '/', () =>
      $('#home').show()
      console.log PawsViewModel
    context.get '/animals', () =>
      $('#home').hide()
      PawsViewModel.AnimalListVM.load()  
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


  resizeAllCarousels = (refresh=true)->
    $('.carousel-scroller').each ->
      if $(this).hasClass 'carousel-rows'
        numRows = Math.min Math.floor(($(window).height()-$(this).parent().offset().top)/$(this).find('li:first').outerHeight(true)), MAX_SCROLLER_ROWS
        resized = resizeCarousel this, numRows, false
      else
        resized = resizeCarousel this, 1, false
      if refresh and resized
        console.log 'Refreshing carousel'
        scrollers[$(this).parent().prop('id')].refresh()

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
