describe('Landing page button', () => {
  beforeEach(() => {
    cy.reload();
    cy.visit('https://silverbullets.rocks')

  })
  it('go on website and all button should work as supposed', () => {

    cy.get('.btn_gioca').click()
    cy.url().should('include', '/board')
    cy.go('back')

    cy.get('.btn_login').click()
    cy.url().should('include', '/login')
    cy.go('back')

    cy.get('.btn_sign').click()
    cy.url().should('include', '/registrati')
    cy.get('a:contains("Silver Bullets")').click();
  })

})