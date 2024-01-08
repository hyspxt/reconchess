describe('Game initialization', () => {
  beforeEach(() => {
    cy.reload();
    cy.visit('https://silverbullets.rocks')

  })
  it('Select a certain game config', () => {

    cy.get('.btn_gioca').click()
    cy.get('.a_bot').click()
    cy.get('.a_human').click()
    cy.get('.a_bot').click()
    cy.get('#bot_3').click()
    cy.get('select#frutta').select('900');
    cy.get('.p_b').click()
    cy.get('#button_start').click()
  })

  it('Select a different game config and move a pawn', () => {

    cy.get('.btn_gioca').click()
    cy.get('.a_bot').click()

    cy.get('#bot_2').click()
    cy.get('select#frutta').select('600');
    cy.get('.p_w').click()
    cy.get('#button_start').click()

    cy.wait(2000);
    cy.get('[data-square="d5"]').click();
    cy.get('[data-square="c2"]').trigger('mousedown', { which: 1 });
    cy.get('[data-square="c4"]').trigger('mousemove');
    cy.get('[data-square="c4"]').trigger('mouseup'), {force: true};
  })

  it('Play as black', () => {

    cy.get('.btn_gioca').click()
    cy.get('.a_bot').click()

    cy.get('#bot_2').click()
    cy.get('select#frutta').select('600');
    cy.get('.p_b').click()
    cy.get('#button_start').click()

    cy.wait(2000);
    cy.get('[data-square="e5"]').click();
    cy.get('[data-square="d2"]').trigger('mousedown', { which: 1 });
    cy.get('[data-square="d2"]').trigger('mousemove');
    cy.get('[data-square="d4"]').trigger('mouseup', { force: true });
  })

})